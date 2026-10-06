import flet as ft
import requests
import base64
import os
import mimetypes

API_URL = "http://127.0.0.1:8000/translate"


class TranslatorApp:

    def __init__(self, page: ft.Page):
        self.page = page
        self.selected_image = None

        self.primary = "#5B5BD6"
        self.secondary = "#7C6FE6"
        self.background = "#F7F6FC"
        self.sidebar_color = "#ECEBFA"
        self.card_color = "#FFFFFF"
        self.text_color = "#29283A"
        self.muted = "#77758A"
        self.success = "#4E9F7A"

        self.english_text = ft.Text(
            "",
            size=20,
            color=self.text_color,
        )

        self.tagalog_text = ft.Text(
            "",
            size=20,
            color=self.text_color,
        )

        self.preview = ft.Image(
            src="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGNgAAAAAgABXQssigAAAABJRU5ErkJggg==",
            width=430,
            height=250,
            fit=ft.BoxFit.CONTAIN,
            visible=False,
            border_radius=15,
        )

        self.loading = ft.ProgressRing(
            visible=False,
            color=self.primary,
        )

        self.status_text = ft.Text(
            "",
            size=14,
            color=self.muted,
        )

        self.file_picker = ft.FilePicker()

        self.content = ft.Container(
            expand=True,
            padding=30,
        )

        self.page.title = "English to Tagalog Translator"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.bgcolor = self.background
        self.page.theme = ft.Theme(font_family="Tahoma")

        self.build_ui()

    def build_ui(self):
        sidebar = ft.Container(
            width=250,
            bgcolor=self.sidebar_color,
            padding=20,
            border_radius=15,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(
                        ft.Icons.TRANSLATE,
                        size=65,
                        color=self.primary,
                    ),
                    ft.Text(
                        "English →\nTagalog",
                        size=25,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                        color=self.text_color,
                    ),
                    ft.Divider(),
                    ft.Button(
                        content="Home",
                        width=190,
                        height=50,
                        bgcolor=self.primary,
                        color=ft.Colors.WHITE,
                        on_click=lambda e: self.show_home(),
                    ),
                    ft.Button(
                        content="English → Tagalog",
                        width=190,
                        height=50,
                        bgcolor=self.secondary,
                        color=ft.Colors.WHITE,
                        on_click=lambda e: self.show_translator(),
                    ),
                    ft.Container(expand=True),
                    ft.Text(
                        "Tesseract OCR",
                        size=14,
                        color=self.muted,
                    ),
                    ft.Text(
                        "Helsinki-NLP",
                        size=14,
                        color=self.muted,
                    ),
                    ft.Text(
                        "FastAPI Backend",
                        size=14,
                        color=self.muted,
                    ),
                    ft.Text(
                        "Flet Desktop App",
                        size=14,
                        color=self.muted,
                    ),
                ],
            ),
        )

        self.content.content = self.home_page()

        self.page.add(
            ft.Row(
                expand=True,
                controls=[
                    sidebar,
                    ft.VerticalDivider(width=1),
                    self.content,
                ],
            )
        )

    def show_home(self):
        self.content.content = self.home_page()
        self.page.update()

    def show_translator(self):
        self.content.content = self.translator_page()
        self.page.update()

    def home_page(self):
        return ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=25,
            controls=[
                ft.Text(
                    "English to Tagalog Translator",
                    size=34,
                    weight=ft.FontWeight.BOLD,
                    color=self.text_color,
                ),
                ft.Text(
                    "OCR-based English text recognition and "
                    "English-to-Tagalog translation",
                    size=18,
                    color=self.muted,
                ),
                ft.Card(
                    bgcolor=self.card_color,
                    content=ft.Container(
                        padding=25,
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    "About the System",
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                    color=self.text_color,
                                ),
                                ft.Text(
                                    "This system captures English text "
                                    "from an image, recognizes the text "
                                    "using Tesseract OCR, and translates "
                                    "the recognized English text into "
                                    "Tagalog using a neural machine "
                                    "translation model.",
                                    size=16,
                                    color=self.text_color,
                                ),
                            ],
                        ),
                    ),
                ),
                ft.Text(
                    "How It Works",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=self.text_color,
                ),
                ft.Row(
                    spacing=20,
                    wrap=True,
                    controls=[
                        self.info_card(
                            ft.Icons.CAMERA_ALT,
                            "Capture Image",
                            "Capture or select an image "
                            "containing English text.",
                        ),
                        self.info_card(
                            ft.Icons.TEXT_FIELDS,
                            "OCR",
                            "Tesseract extracts the "
                            "English text from the image.",
                        ),
                        self.info_card(
                            ft.Icons.TRANSLATE,
                            "Translate",
                            "The recognized English text "
                            "is translated into Tagalog.",
                        ),
                        self.info_card(
                            ft.Icons.CHECK_CIRCLE,
                            "Display",
                            "The English and Tagalog "
                            "results are displayed.",
                        ),
                    ],
                ),
                ft.Text(
                    "Technologies Used",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=self.text_color,
                ),
                ft.Row(
                    spacing=15,
                    wrap=True,
                    controls=[
                        ft.Chip(label=ft.Text("Tesseract OCR")),
                        ft.Chip(label=ft.Text("Helsinki-NLP")),
                        ft.Chip(label=ft.Text("FastAPI")),
                        ft.Chip(label=ft.Text("Flet")),
                        ft.Chip(label=ft.Text("Python")),
                    ],
                ),
            ],
        )

    def info_card(self, icon, title, description):
        return ft.Card(
            bgcolor=self.card_color,
            content=ft.Container(
                width=210,
                padding=20,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(
                            icon,
                            size=45,
                            color=self.primary,
                        ),
                        ft.Text(
                            title,
                            size=17,
                            weight=ft.FontWeight.BOLD,
                            color=self.text_color,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            description,
                            size=14,
                            color=self.muted,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                ),
            ),
        )

    def translator_page(self):
        return ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
            controls=[
                ft.Text(
                    "English → Tagalog",
                    size=34,
                    weight=ft.FontWeight.BOLD,
                    color=self.text_color,
                ),
                ft.Text(
                    "Capture an image containing English "
                    "text and translate it into Tagalog.",
                    size=18,
                    color=self.muted,
                ),
                ft.Row(
                    spacing=25,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Card(
                            bgcolor=self.card_color,
                            content=ft.Container(
                                width=500,
                                padding=25,
                                content=ft.Column(
                                    spacing=15,
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    ft.Icons.LANGUAGE,
                                                    color=self.primary,
                                                ),
                                                ft.Text(
                                                    "English",
                                                    size=22,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=self.text_color,
                                                ),
                                            ],
                                        ),
                                        ft.Divider(),
                                        ft.Container(
                                            width=450,
                                            height=180,
                                            padding=15,
                                            bgcolor=self.background,
                                            border_radius=12,
                                            content=self.english_text,
                                        ),
                                        ft.Text(
                                            "Captured Image",
                                            size=17,
                                            weight=ft.FontWeight.BOLD,
                                            color=self.text_color,
                                        ),
                                        ft.Container(
                                            width=450,
                                            height=250,
                                            bgcolor=self.background,
                                            border_radius=12,
                                            alignment=ft.Alignment.CENTER,
                                            content=self.preview,
                                        ),
                                        ft.Button(
                                            content="Choose Image",
                                            width=450,
                                            height=48,
                                            bgcolor=self.secondary,
                                            color=ft.Colors.WHITE,
                                            on_click=self.choose_image,
                                        ),
                                    ],
                                ),
                            ),
                        ),
                        ft.Card(
                            bgcolor=self.card_color,
                            content=ft.Container(
                                width=500,
                                padding=25,
                                content=ft.Column(
                                    spacing=15,
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    ft.Icons.TRANSLATE,
                                                    color=self.primary,
                                                ),
                                                ft.Text(
                                                    "Tagalog",
                                                    size=22,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=self.text_color,
                                                ),
                                            ],
                                        ),
                                        ft.Divider(),
                                        ft.Container(
                                            width=450,
                                            height=180,
                                            padding=15,
                                            bgcolor=self.background,
                                            border_radius=12,
                                            content=self.tagalog_text,
                                        ),
                                        ft.Container(height=260),
                                        ft.Button(
                                            content="Capture & Translate",
                                            width=450,
                                            height=52,
                                            bgcolor=self.primary,
                                            color=ft.Colors.WHITE,
                                            on_click=self.translate,
                                        ),
                                        ft.Row(
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            controls=[
                                                self.loading,
                                                self.status_text,
                                            ],
                                        ),
                                    ],
                                ),
                            ),
                        ),
                    ],
                ),
            ],
        )

    async def choose_image(self, e):
        files = await self.file_picker.pick_files(
            allow_multiple=False,
        )

        if not files:
            return

        selected_file = files[0]
        self.selected_image = selected_file.path

        if not self.selected_image or not os.path.isfile(self.selected_image):
            self.status_text.value = "Unable to access the selected image."
            self.page.update()
            return

        with open(self.selected_image, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")

        self.preview.src = encoded
        self.preview.visible = True

        self.english_text.value = ""
        self.tagalog_text.value = ""
        self.status_text.value = "Image selected."

        self.page.update()

    def translate(self, e):
        if self.selected_image is None:
            self.status_text.value = "Please choose an image first."
            self.page.update()
            return

        self.loading.visible = True
        self.status_text.value = "Processing image..."
        self.english_text.value = ""
        self.tagalog_text.value = ""
        self.page.update()

        try:
            mime_type = mimetypes.guess_type(self.selected_image)[0]
            if not mime_type:
                mime_type = "application/octet-stream"

            with open(self.selected_image, "rb") as f:
                response = requests.post(
                    API_URL,
                    files={
                        "file": (
                            os.path.basename(self.selected_image),
                            f,
                            mime_type,
                        )
                    },
                    timeout=180,
                )

            response.raise_for_status()
            data = response.json()

            self.english_text.value = data.get("english_text", "")
            self.tagalog_text.value = data.get("tagalog_text", "")

            if not self.english_text.value:
                self.status_text.value = "No text detected."
            else:
                self.status_text.value = "Translation complete."

        except requests.exceptions.ConnectionError:
            self.status_text.value = (
                "Cannot connect to FastAPI. "
                "Make sure the backend is running."
            )
        except requests.exceptions.Timeout:
            self.status_text.value = "The request took too long."
        except requests.exceptions.HTTPError as ex:
            self.status_text.value = f"Backend error: {ex}"
        except ValueError:
            self.status_text.value = "Backend returned invalid JSON."
        except Exception as ex:
            self.status_text.value = f"Error: {ex}"
        finally:
            self.loading.visible = False
            self.page.update()


def main(page: ft.Page):
    TranslatorApp(page)


if __name__ == "__main__":
    ft.run(
        main,
        assets_dir="assets",
    )
