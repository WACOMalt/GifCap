use image::RgbaImage;
use std::time::{Duration, Instant};

use std::sync::Arc;

#[derive(Clone)]
pub struct Frame {
    pub image: RgbaImage,
    pub timestamp: Duration, // Relative to session start
}

#[derive(Clone)]
pub struct RecordingSession {
    frames: Vec<Arc<Frame>>,
    start_time: Instant,
}

impl RecordingSession {
    pub fn new() -> Self {
        Self {
            frames: Vec::new(),
            start_time: Instant::now(),
        }
    }
    
    pub fn add_frame(&mut self, image: RgbaImage) {
        let timestamp = self.start_time.elapsed();
        self.frames.push(Arc::new(Frame { image, timestamp }));
    }
    
    pub fn frame_count(&self) -> usize {
        self.frames.len()
    }
    
    #[allow(dead_code)]
    pub fn clear(&mut self) {
        self.frames.clear();
        self.start_time = Instant::now();
    }

    pub fn remove_frame(&mut self, index: usize) {
        if index < self.frames.len() {
            self.frames.remove(index);
        }
    }

    pub fn frames(&self) -> &[Arc<Frame>] {
        &self.frames
    }

    pub fn get_frame_delay(&self, index: usize) -> Duration {
        if index + 1 < self.frames.len() {
            self.frames[index+1].timestamp - self.frames[index].timestamp
        } else {
            Duration::from_millis(100) // Default for last frame
        }
    }

    pub fn set_delay(&mut self, index: usize, delay: Duration) {
        if index < self.frames.len() {
            // Note: We need to modify the frame or subsequent timestamps.
            // Since frames are now Arc, we must clone if we want to mutate specific frame data?
            // Actually, Frame only stores image and timestamp.
            // set_delay modifies timestamps of *subsequent* frames usually?
            // "next_ts = current_ts + delay".
            // Implementation modified timestamps of SUBSEQUENT frames.
            // We need &mut Arc<Frame>.
            // Arc::make_mut will clone if shared... wait.
            // If we clone the session, we share frames.
            // If we modify timestamps in the editor, we effectively fork the timeline.
            // So we SHOULD clone the frames that are affected.
            // Arc::make_mut is perfect.
            
            if index + 1 < self.frames.len() {
                let old_next_ts = self.frames[index+1].timestamp;
                let base_ts = self.frames[index].timestamp;
                let new_next_ts = base_ts + delay;
                
                if new_next_ts > old_next_ts {
                     let shift = new_next_ts - old_next_ts;
                     for f in self.frames.iter_mut().skip(index + 1) {
                         let frame_mut = Arc::make_mut(f);
                         frame_mut.timestamp += shift;
                     }
                } else {
                     let shift = old_next_ts - new_next_ts;
                     for f in self.frames.iter_mut().skip(index + 1) {
                         let frame_mut = Arc::make_mut(f);
                         frame_mut.timestamp = frame_mut.timestamp.saturating_sub(shift);
                         if frame_mut.timestamp < base_ts {
                             frame_mut.timestamp = base_ts;
                         }
                     }
                }
            }
        }
    }

    pub fn save_to_file<P: AsRef<std::path::Path>>(&self, path: P) -> Result<(), Box<dyn std::error::Error>> {
        use std::fs::File;
        use image::codecs::gif::GifEncoder;
        use image::{Frame as ImageFrame, Delay};

        let file = File::create(path)?;
        // Speed optimization: 1 (slow, best quality) to 30 (fast, lower quality)
        // 30 is much faster for screen recording save times.
        let mut encoder = GifEncoder::new_with_speed(file, 30);
        
        encoder.set_repeat(image::codecs::gif::Repeat::Infinite)?; 

        for (i, frame) in self.frames.iter().enumerate() {
            // Calculate delay
            let delay_duration = if i + 1 < self.frames.len() {
                self.frames[i+1].timestamp - frame.timestamp
            } else {
                Duration::from_millis(100) // Default 10FPS for last frame
            };
            
            let delay = Delay::from_saturating_duration(delay_duration);
            
            // Convert RgbaImage to Frame (which clones data usually)
            // frame is &Arc<Frame>. frame.image is RgbaImage.
            let image_frame = ImageFrame::from_parts(frame.image.clone(), 0, 0, delay);
            
            encoder.encode_frame(image_frame)?;
        }
        
        Ok(())
    }
}
