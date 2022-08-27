from django.templatetags.static import static

# Configures the x-logo information for Redoc / OpenAPI
X_LOGO_INFO = {
    'url': static('images/logo.png'),
    'altText': 'My Project',
    'backgroundColor': 'rgb(250, 250, 250)',
    'href': 'https://example.com',
}
