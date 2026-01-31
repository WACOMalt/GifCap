use iced::widget::{button, column, container, row, text, text_input};
use iced::{Element, Length, Theme, Color, Font};

pub struct Recorder {
    pub is_recording: bool,
    fps: u64,
    fps_text: String,
}

#[derive(Debug, Clone)]
pub enum Message {
    RecordPressed,
    StopPressed,
    FramePressed,
    EditPressed,
    SavePressed,
    FpsChanged(String),
}

impl Recorder {
    pub fn new() -> Self {
        Self {
            is_recording: false,
            fps: 15, // Default to 15 FPS
            fps_text: "15".to_string(),
        }
    }

    pub fn is_recording(&self) -> bool {
        self.is_recording
    }
    
    pub fn fps(&self) -> u64 {
        self.fps
    }

    pub fn update(&mut self, message: Message) {
        match message {
            Message::RecordPressed => self.is_recording = true,
            Message::StopPressed => self.is_recording = false,
            Message::FpsChanged(val) => {
                 // Allow typing numbers, refuse non-numbers (except empty for editing)
                 if val.is_empty() {
                     self.fps_text = val;
                     // Don't update numerical FPS yet or default to something? 
                     // Let's keep previous FPS until valid number.
                 } else if val.chars().all(|c| c.is_numeric()) {
                     self.fps_text = val.clone();
                     if let Ok(num) = val.parse::<u64>() {
                         // Clamp for sanity? 
                         // maybe > 0.
                         if num > 0 {
                            self.fps = num;
                         }
                     }
                 }
            },
            _ => {}
        }
    }

    pub fn view(&self) -> Element<Message> {
        // Control Panel (Right side buttons)
        let rec_btn_text = if self.is_recording { "Stop" } else { "Rec" };
        let rec_msg = if self.is_recording { Message::StopPressed } else { Message::RecordPressed };
        let rec_style = if self.is_recording { iced::theme::Button::Destructive } else { iced::theme::Button::Secondary };

        let make_text = |content: &str| {
            text(content)
                .font(Font::with_name("Comfortaa"))
                .size(14)
                .horizontal_alignment(iced::alignment::Horizontal::Center)
        };

        // Handle Edit button state
        // Default Edit button to Secondary
        let mut edit_btn = button(make_text("Edit"))
            .width(Length::Fill)
            .style(iced::theme::Button::Secondary); 
            
        if !self.is_recording {
             edit_btn = edit_btn.on_press(Message::EditPressed);
        }
        
        // FPS Input
        let fps_input = text_input("FPS", &self.fps_text)
            .on_input(Message::FpsChanged)
            .size(12)
            .width(Length::Fill)
            .padding(5);

        let controls = column![
            button(make_text(rec_btn_text)).on_press(rec_msg).style(rec_style).width(Length::Fill),
            text("FPS").size(12),
            fps_input,
            button(make_text("Frame"))
                .on_press(Message::FramePressed)
                .style(iced::theme::Button::Secondary)
                .width(Length::Fill),
            edit_btn,
            button(make_text("Save"))
                .on_press(Message::SavePressed)
                .style(iced::theme::Button::Secondary)
                .width(Length::Fill),
        ]
        .spacing(5)
        .padding(5)
        .width(Length::Fixed(80.0));

        // Main layout: "Hole" + Controls
        row![
            // The transparent cutout
            container(row![]) 
                .width(Length::Fill)
                .height(Length::Fill)
                .style(|_theme: &Theme| container::Appearance {
                    border: iced::Border {
                        width: 2.0,
                        color: Color::from_rgb8(100, 100, 100),
                        radius: 0.0.into(),
                    },
                    ..Default::default()
                }),
            
            // Right side controls
            container(controls)
                .height(Length::Fill)
                .style(|_theme: &Theme| container::Appearance {
                    background: Some(Color::from_rgb8(45, 45, 45).into()),
                    text_color: Some(Color::WHITE),
                    ..Default::default()
                })
        ]
        .into()
    }
}
