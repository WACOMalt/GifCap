mod ui;
mod capture;
mod recording;

use iced::widget::container; // Kept container locally used? No, view maps directly. Actually main doesn't use widgets directly anymore.
// Checking lines: view() calls self.recorder.view()
// main() uses Settings
// So clean up:
use iced::{executor, time, window, Application, Command, Element, Event, Settings, Subscription, Theme};
use std::time::{Instant, Duration};
use std::sync::{Arc, Mutex}; // Added for thread safety
use ui::recorder::{self, Recorder};
use capture::CaptureManager;
use recording::RecordingSession;
use image::RgbaImage;

pub fn main() -> iced::Result {
    env_logger::init();

    GifCap::run(Settings {
        fonts: vec![include_bytes!("../resources/fonts/Comfortaa-Regular.ttf").into()],
        default_font: iced::Font::with_name("Comfortaa"),
        default_text_size: 16.0.into(),
        window: iced::window::Settings {
            size: iced::Size::new(600.0, 400.0),
            decorations: true,      // Native borders restored
            transparent: true,      // Keep transparency for the hole
            exit_on_close_request: true, // Let OS handle close
            ..Default::default()
        },
        ..Default::default()
    })
}

struct GifCap {
    recorder: Recorder,
    editor: Option<ui::editor::Editor>,
    window_position: Option<iced::Point>,
    window_size: iced::Size,
    session: Option<RecordingSession>,
    capturing: bool,
    capture_manager: Arc<Mutex<CaptureManager>>,
}

#[derive(Debug, Clone)]
enum Message {
    Recorder(recorder::Message),
    Editor(ui::editor::Message),
    Tick(Instant),
    Event(Event),
    FrameCaptured(Result<Option<RgbaImage>, String>),
    FileSaved(Result<(), String>),
}

impl Application for GifCap {
    type Executor = executor::Default;
    type Message = Message;
    type Theme = Theme;
    type Flags = ();

    fn new(_flags: ()) -> (Self, Command<Message>) {
        (
            GifCap {
                recorder: {
                    let mut r = Recorder::new();
                    r.is_recording = false;
                    r
                },
                editor: None,
                window_position: None,
                window_size: iced::Size::new(600.0, 400.0),
                session: None,
                capturing: false,
                capture_manager: Arc::new(Mutex::new(CaptureManager::new())),
            },
            Command::none(),
        )
    }

    fn title(&self) -> String {
        String::from("GifCap")
    }

    fn update(&mut self, message: Message) -> Command<Message> {
        match message {
            Message::Recorder(msg) => {
                match msg {
                    recorder::Message::RecordPressed => {
                         if self.session.is_none() {
                             self.session = Some(RecordingSession::new());
                         }
                    }
                    recorder::Message::StopPressed => {
                        // Ensure we finalize anything if needed
                        if let Ok(manager) = self.capture_manager.lock() {
                            manager.stop_capture();
                        }
                    }
                    recorder::Message::EditPressed => {
                        // Switch to Editor mode
                        if let Some(session) = self.session.take() {
                            self.editor = Some(ui::editor::Editor::new(session));
                            // Resize window for editor? Maybe not yet.
                        }
                    }
                    recorder::Message::SavePressed => {
                        if let Some(session) = &self.session {
                            return self.save_session(session);
                        }
                    }
                    _ => {}
                }
                
                self.recorder.update(msg);
                Command::none()
            }
            Message::Editor(msg) => {
                match msg {
                    ui::editor::Message::Back => {
                        // Exit editor, restore session
                        if let Some(editor) = self.editor.take() {
                            self.session = Some(editor.into_session());
                        }
                    }
                    ui::editor::Message::Save => {
                        if let Some(editor) = &self.editor {
                            return self.save_session(editor.session());
                        }
                    }
                    _ => {
                         if let Some(editor) = &mut self.editor {
                             editor.update(msg);
                         }
                    }
                }
                Command::none()
            }
            Message::Event(Event::Window(_, window::Event::CloseRequested)) => {
                window::close(iced::window::Id::MAIN)
            }
// ... (Keep existing handlers for Moved, Resized, Tick, FrameCaptured, FileSaved)
            Message::Event(Event::Window(_, window::Event::Moved { x, y })) => {
                self.window_position = Some(iced::Point::new(x as f32, y as f32));
                Command::none()
            }
            Message::Event(Event::Window(_, window::Event::Resized { width, height })) => {
                self.window_size = iced::Size::new(width as f32, height as f32);
                Command::none()
            }
            Message::Event(_) => Command::none(),
            Message::Tick(_) => {
                // If in editor mode, do NOT record
                if self.editor.is_some() {
                    return Command::none();
                }

                if self.recorder.is_recording() {
// ... (Existing Tick logic)
                    // Check for congestion
                    if self.capturing {
                        return Command::none();
                    }
                    
                    // Start session if not exists
                    if self.session.is_none() {
                        self.session = Some(RecordingSession::new());
                    }
                    
                    if let Some(pos) = self.window_position {
                        self.capturing = true;
                        
                        let x = pos.x as i32;
                        let y = pos.y as i32;
                        let w = self.window_size.width as u32;
                        let h = self.window_size.height as u32;
                        
                        // Clone the Arc to move into the thread
                        let capture_manager = self.capture_manager.clone();
                        
                        // Async capture
                        return Command::perform(async move {
                            tokio::task::spawn_blocking(move || {
                                // Capture logic
                                let controls_width = 80; 
                                
                                let capture_x = x;
                                let capture_y = y; 
                                
                                let capture_w = w.saturating_sub(controls_width);
                                let capture_h = h;
                                
                                if capture_w > 0 && capture_h > 0 {
                                    // Lock the mutex to access mutable CaptureManager
                                    // Handle poisoned mutex by recovering
                                    let manager = match capture_manager.lock() {
                                        Ok(guard) => guard,
                                        Err(poisoned) => {
                                            eprintln!("WARNING: Mutex poisoned, recovering...");
                                            poisoned.into_inner()
                                        }
                                    };
                                    
                                    let start = std::time::Instant::now();
                                    let res = manager.capture_area(capture_x, capture_y, capture_w, capture_h);
                                    let duration = start.elapsed();
                                    if duration.as_millis() > 20 {
                                         println!("Slow capture: {:?}", duration);
                                    }

                                    res.map(Some)
                                        .map_err(|e| e.to_string())
                                } else {
                                    Ok(None)
                                }
                            }).await.unwrap_or_else(|e| Err(e.to_string()))
                        }, Message::FrameCaptured);
                    }
                }
                Command::none()
            }
            Message::FrameCaptured(result) => {
                self.capturing = false;
                match result {
                    Ok(Some(image)) => {
                        // Only save if we are still recording AND NOT IN EDITOR
                        if self.recorder.is_recording() && self.editor.is_none() {
                            if let Some(session) = &mut self.session {
                                session.add_frame(image);
                                println!("Captured frame: {} | Total: {}", session.frame_count(), session.frame_count());
                            }
                        }
                    }
                    Ok(None) => {} // Skipped
                    Err(e) => eprintln!("Capture failed: {}", e),
                }
                Command::none()
            }
            Message::FileSaved(result) => {
                match result {
                    Ok(_) => println!("Saved successfully!"),
                    Err(e) => eprintln!("Error saving: {}", e),
                }
                Command::none()
            }
        }
    }

    fn view(&self) -> Element<Message> {
        if let Some(editor) = &self.editor {
            return container(editor.view().map(Message::Editor))
                .width(iced::Length::Fill)
                .height(iced::Length::Fill)
                .style(|_theme: &Theme| container::Appearance {
                    background: Some(iced::Color::WHITE.into()), // Opaque background for editor
                    ..Default::default()
                })
                .into();
        }

        // Enforce transparent background for the main window container
        container(self.recorder.view().map(Message::Recorder))
            .width(iced::Length::Fill)
            .height(iced::Length::Fill)
            .style(|_theme: &Theme| container::Appearance {
                background: Some(iced::Color::TRANSPARENT.into()),
                ..Default::default()
            })
            .into()
    }

    fn style(&self) -> iced::theme::Application {
        iced::theme::Application::Custom(Box::new(|_theme: &Theme| iced::application::Appearance {
            background_color: iced::Color::TRANSPARENT,
            text_color: iced::Color::BLACK,
        }))
    }

    fn subscription(&self) -> Subscription<Message> {
        let tick = if self.recorder.is_recording() {
            let fps = self.recorder.fps();
            // Avoid division by zero, though picker ensures >= 10
            let fps = if fps == 0 { 15 } else { fps };
            
            time::every(Duration::from_millis(1000 / fps)).map(Message::Tick)
        } else {
            Subscription::none()
        };
        
        let events = iced::event::listen().map(Message::Event);
        
        Subscription::batch(vec![tick, events])
    }
}

impl GifCap {
    fn save_session(&self, session: &RecordingSession) -> Command<Message> {
        if session.frame_count() > 0 {
            // Open file dialog
            let path = rfd::FileDialog::new()
                .add_filter("GIF", &["gif"])
                .set_file_name("recording.gif")
                .save_file();
            
            if let Some(path) = path {
                println!("Starting save to {:?}", path);
                
                let session = session.clone(); 
                
                return Command::perform(async move {
                    tokio::task::spawn_blocking(move || {
                        session.save_to_file(&path)
                            .map_err(|e| e.to_string())
                    }).await.unwrap_or_else(|e| Err(e.to_string()))
                }, Message::FileSaved);
            }
        } else {
            println!("No frames to save.");
        }
        Command::none()
    }
    
}
