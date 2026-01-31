use iced::widget::{button, column, container, row, scrollable, text, text_input, Image};
use iced::{Element, Length, Alignment, Color};
use iced::widget::image::Handle;
use std::time::Duration;
use crate::recording::RecordingSession;

#[derive(Debug, Clone)]
pub enum Message {
    Back,
    Save,
    DeleteFrame,
    FrameSelected(usize),
    DelayInputChanged(String),
    SetDelay,
}

pub struct Editor {
    session: RecordingSession,
    thumbnails: Vec<Handle>,
    selected_frame: Option<usize>,
    delay_input: String,
}

impl Editor {
    pub fn new(session: RecordingSession) -> Self {
        let thumbnails = session.frames().iter().map(|frame| {
            let width = frame.image.width();
            let height = frame.image.height();
            let pixels = frame.image.clone().into_raw();
            Handle::from_pixels(width, height, pixels)
        }).collect();

        Self {
            session,
            thumbnails,
            selected_frame: None,
            delay_input: "100".to_string(),
        }
    }

    pub fn update(&mut self, message: Message) {
        match message {
            Message::FrameSelected(index) => {
                self.selected_frame = Some(index);
                // Update delay input to current frame's delay
                let ms = self.session.get_frame_delay(index).as_millis();
                self.delay_input = ms.to_string();
            }
            Message::DeleteFrame => {
                if let Some(index) = self.selected_frame {
                    self.session.remove_frame(index);
                    self.thumbnails.remove(index);
                    
                    // Adjust selection
                    if self.thumbnails.is_empty() {
                        self.selected_frame = None;
                    } else if index >= self.thumbnails.len() {
                        self.selected_frame = Some(self.thumbnails.len() - 1);
                    }
                }
            }
            Message::DelayInputChanged(val) => {
                if val.chars().all(|c| c.is_numeric()) {
                    self.delay_input = val;
                }
            }
            Message::SetDelay => {
                if let Some(index) = self.selected_frame {
                    if let Ok(ms) = self.delay_input.parse::<u64>() {
                        self.session.set_delay(index, Duration::from_millis(ms));
                    }
                }
            }
            _ => {}
        }
    }

    pub fn view(&self) -> Element<Message> {
        let frame_strip: Element<Message> = if self.thumbnails.is_empty() {
             container(text("No frames"))
                .width(Length::Fill)
                .height(Length::Fixed(150.0))
                .center_x()
                .center_y()
                .into()
        } else {
            let images: Element<Message> = row(
                self.thumbnails.iter().enumerate().map(|(i, handle)| {
                    let is_selected = self.selected_frame == Some(i);
                    let image = Image::new(handle.clone()).height(Length::Fixed(100.0));
                    
                    // Wrap in button for selection
                    let content = container(image)
                        .padding(2)
                        .style(move |_theme: &iced::Theme| container::Appearance {
                            border: iced::Border {
                                width: if is_selected { 3.0 } else { 1.0 },
                                color: if is_selected { Color::from_rgb(0.0, 0.8, 0.0) } else { Color::WHITE },
                                radius: 0.0.into(),
                            },
                            ..Default::default()
                        });

                    button(content)
                        .on_press(Message::FrameSelected(i))
                        .padding(0)
                        .style(iced::theme::Button::Text) // Transparent button
                        .into()
                }).collect::<Vec<_>>()
            ).spacing(10).into();

            scrollable(images)
                .direction(scrollable::Direction::Horizontal(scrollable::Properties::default()))
                .height(Length::Fixed(140.0))
                .into()
        };

        let controls = row![
            button("Delete Selected").on_press(Message::DeleteFrame),
            text("Delay (ms):"),
            text_input("100", &self.delay_input)
                .on_input(Message::DelayInputChanged)
                .width(Length::Fixed(60.0)),
            button("Set").on_press(Message::SetDelay),
        ]
        .spacing(10)
        .align_items(Alignment::Center);

        let content = column![
            text("Editor Mode").size(20),
            frame_strip,
            controls,
            row![
                button("Resume Recording").on_press(Message::Back),
                button("Save GIF").on_press(Message::Save),
            ]
            .spacing(10)
        ]
        .spacing(20)
        .padding(20)
        .align_items(Alignment::Center);

        container(content)
            .width(Length::Fill)
            .height(Length::Fill)
            .center_x()
            .center_y()
            .into()
    }
    
    pub fn session(&self) -> &RecordingSession {
        &self.session
    }

    pub fn into_session(self) -> RecordingSession {
        self.session
    }
}
