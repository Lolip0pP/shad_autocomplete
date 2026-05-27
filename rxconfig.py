import reflex as rx

config = rx.Config(
    app_name="shad_autocomplete",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)