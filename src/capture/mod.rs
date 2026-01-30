use image::RgbaImage;
use std::error::Error;
use scap::capturer::{Capturer, Options};
use device_query::{DeviceQuery, DeviceState};
use std::sync::mpsc;
use std::thread;

enum CaptureCommand {
    Capture {
        x: i32,
        y: i32,
        width: u32,
        height: u32,
        response: mpsc::Sender<Result<RgbaImage, String>>,
    },
    Stop,
}

pub struct CaptureManager {
    tx: mpsc::Sender<CaptureCommand>,
}

impl CaptureManager {
    pub fn new() -> Self {
        // Platform Support Check (Main thread check)
        if !scap::is_supported() {
            eprintln!("❌ Platform not supported via SCAP");
        }
        
        // Permission Check
        if !scap::has_permission() {
             scap::request_permission(); 
        }

        let (tx, rx) = mpsc::channel::<CaptureCommand>();

        thread::spawn(move || {
            let mut capturer: Option<Capturer> = None;
            let mut _monitor_origin = (0, 0);

            // Pre-check targets in worker thread
            let targets = scap::get_all_targets().unwrap_or_else(|_| vec![]);

            // Try to find monitor origin
            if let Some(_target) = targets.first() {
                // Assuming first target is primary for now. 
                // Scap target structure inspection needed if we want precise origin.
                // For now, (0,0).
            }

            while let Ok(cmd) = rx.recv() {
                match cmd {
                    CaptureCommand::Stop => {
                        // Drop the capturer to stop the engine and close the channel
                        capturer = None;
                    }
                    CaptureCommand::Capture { x, y, width, height, response } => {
                        let res = (|| -> Result<RgbaImage, String> {
                            // Init Capturer if needed
                            if capturer.is_none() {
                                let options = Options {
                                    fps: 60,
                                    target: None, 
                                    show_cursor: false, 
                                    show_highlight: false,
                                    output_type: scap::frame::FrameType::BGRAFrame,
                                    ..Default::default()
                                };
                                let mut c = Capturer::build(options).map_err(|e| e.to_string())?;
                                c.start_capture();
                                capturer = Some(c);
                            }

                            let c = capturer.as_mut().unwrap();
                            let frame = c.get_next_frame().map_err(|e| e.to_string())?;

                            let (w, h, data) = match frame {
                                scap::frame::Frame::BGRA(f) => (f.width as u32, f.height as u32, f.data),
                                scap::frame::Frame::BGRx(f) => (f.width as u32, f.height as u32, f.data),
                                _ => return Err("Unexpected frame format".to_string()),
                            };

                            // BGRA -> RGBA Swizzle
                            let mut rgba_data = data;
                            for chunk in rgba_data.chunks_exact_mut(4) {
                                let b = chunk[0];
                                let r = chunk[2];
                                chunk[0] = r;
                                chunk[2] = b;
                                chunk[3] = 255; // Force Alpha to 255 (Opaque) to fix "invisible" X11 capture
                            }

                            let mut caught_image = RgbaImage::from_raw(w, h, rgba_data)
                                .ok_or("Failed to create image buffer")?;

                            // Draw Cursor
                            Self::draw_cursor_on_image(&mut caught_image, 0, 0);

                            // Crop
                            let mw = caught_image.width();
                            let mh = caught_image.height();
                            let crop_x = x.max(0) as u32;
                            let crop_y = y.max(0) as u32;

                            if crop_x + width <= mw && crop_y + height <= mh {
                                Ok(image::imageops::crop(&mut caught_image, crop_x, crop_y, width, height).to_image())
                            } else {
                                let safe_w = (mw as i32 - x).max(0).min(width as i32) as u32;
                                let safe_h = (mh as i32 - y).max(0).min(height as i32) as u32;
                                if safe_w > 0 && safe_h > 0 {
                                     Ok(image::imageops::crop(&mut caught_image, crop_x, crop_y, safe_w, safe_h).to_image())
                                } else {
                                     Err("Capture area completely out of bounds".to_string())
                                }
                            }
                        })();

                        let _ = response.send(res);
                    }
                }
            }
        });

        Self { tx }
    }

    pub fn stop_capture(&self) {
        let _ = self.tx.send(CaptureCommand::Stop);
    }

    pub fn capture_area(&self, x: i32, y: i32, width: u32, height: u32) -> Result<RgbaImage, Box<dyn Error + Send + Sync>> {
        let (resp_tx, resp_rx) = mpsc::channel();
        self.tx.send(CaptureCommand::Capture { x, y, width, height, response: resp_tx })
            .map_err(|_| "Capture thread is dead")?;
        
        match resp_rx.recv() {
            Ok(Ok(img)) => Ok(img),
            Ok(Err(s)) => Err(s.into()),
            Err(_) => Err("Failed to receive response from capture thread".into()),
        }
    }

    fn draw_cursor_on_image(image: &mut RgbaImage, monitor_x: i32, monitor_y: i32) {
        // We perform the device query content on the worker thread too.
        // It might be better to do it on finding the cursor pos, but doing it here is fine.
        let device_state = DeviceState::new();
        let mouse = device_state.get_mouse();
        
        let global_mx = mouse.coords.0;
        let global_my = mouse.coords.1;

        let img_mx = global_mx - monitor_x;
        let img_my = global_my - monitor_y;

        let cursor_shape: [[u8; 12]; 19] = [
            [1,0,0,0,0,0,0,0,0,0,0,0],
            [1,1,0,0,0,0,0,0,0,0,0,0],
            [1,2,1,0,0,0,0,0,0,0,0,0],
            [1,2,2,1,0,0,0,0,0,0,0,0],
            [1,2,2,2,1,0,0,0,0,0,0,0],
            [1,2,2,2,2,1,0,0,0,0,0,0],
            [1,2,2,2,2,2,1,0,0,0,0,0],
            [1,2,2,2,2,2,2,1,0,0,0,0],
            [1,2,2,2,2,2,2,2,1,0,0,0],
            [1,2,2,2,2,2,2,2,2,1,0,0],
            [1,2,2,2,2,2,1,1,1,1,0,0],
            [1,2,2,1,2,2,1,0,0,0,0,0],
            [1,2,1,0,1,2,2,1,0,0,0,0],
            [1,1,0,0,1,2,2,1,0,0,0,0],
            [1,0,0,0,0,1,2,2,1,0,0,0],
            [0,0,0,0,0,1,2,2,1,0,0,0],
            [0,0,0,0,0,0,1,2,1,0,0,0],
            [0,0,0,0,0,0,0,1,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0],
        ];

        let w = image.width() as i32;
        let h = image.height() as i32;

        for (row_idx, row) in cursor_shape.iter().enumerate() {
            let cy = img_my + row_idx as i32;
            if cy < 0 || cy >= h { continue; }
            
            for (col_idx, &pixel_type) in row.iter().enumerate() {
                let cx = img_mx + col_idx as i32;
                if cx < 0 || cx >= w { continue; }

                if pixel_type == 1 {
                     image.put_pixel(cx as u32, cy as u32, image::Rgba([0, 0, 0, 255]));
                } else if pixel_type == 2 {
                     image.put_pixel(cx as u32, cy as u32, image::Rgba([255, 255, 255, 255]));
                }
            }
        }
    }
}
