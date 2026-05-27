"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from rxconfig import config
from llm_client import get_autocomplete_suggestion


class State(rx.State):
    """The app state."""

    user_input: str = ""
    suggestion: str = ""
    is_loading: bool = False

    def handle_input_change(self, text: str):
        """Попробуем не вызывать модель слишком часто и без повода"""
        self.user_input = text

        if len(text) < 3:
            self.suggestion = ""
            return

        self.is_loading = True
        # В реальном приложении лучше сделать асинхронный вызов, пока так
        self.suggestion = get_autocomplete_suggestion(text)
        self.is_loading = False

    def accept_suggestion(self):
        """Применяет подсказку при клике на нее или по Tab."""
        if self.suggestion:
            self.user_input = f"{self.user_input.rstrip()} {self.suggestion.lstrip()}"
            self.suggestion = ""


def index() -> rx.Component:
    """Это писал Gemini"""
    return rx.center(
        rx.vstack(
            rx.heading("LLM Real-time Autocomplete", size="7", margin_bottom="1rem"),
            rx.text("Начните вводить текст, и Qwen-3.5-9B предложит продолжение:", color_scheme="gray"),
            # Контейнер для ввода и подсказки
            rx.box(
                rx.input(
                    value=State.user_input,
                    on_change=State.handle_input_change,
                    placeholder="Начните писать что-нибудь...",
                    width="500px",
                    size="3",
                ),
                width="100%",
            ),
            # Блок отображения подсказки
            rx.cond(
                State.suggestion,
                rx.card(
                    rx.hstack(
                        rx.text(f"Предагаемое продолжение: {State.suggestion}", font_style="italic"),
                        rx.button(
                            "Добавить", on_click=State.accept_suggestion, size="1", color_scheme="green"
                        ),
                        align="center",
                        justify="between",
                    ),
                    width="500px",
                    variant="ghost",
                    background_color="var(--accent-2)",
                ),
            ),
            # Индикатор загрузки
            rx.cond(State.is_loading, rx.spinner(size="3")),
            spacing="4",
            padding="2rem",
            border_radius="15px",
            box_shadow="lg",
            background_color="var(--gray-2)",
        ),
        height="100vh",
    )


app = rx.App()
app.add_page(index)
