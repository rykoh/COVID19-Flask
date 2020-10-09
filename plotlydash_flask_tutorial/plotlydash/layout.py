"""Plotly Dash HTML layout override."""

html_layout = '''
<!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
        </head>
        <body class="dash-template">
            <!--
            <header>
                <div class="nav-wrapper">
                    <a href="/">
                        <img src="/static/img/fibonnaci_dots.png" class="logo" />
                        <h1>COVID-19 Student Research Opportunities</h1>
                    </a>
                    <nav>
                        <a href="/html/">HTML</a> |
                        <a href="/css/">CSS</a> |
                        <a href="/js/">JavaScript</a> |
                        <a href="/python/">Python</a>
                    </nav>
                </div> 
            </header>
            -->
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
            <style>
                .footer {
                    position: relative;
                    left: 0;
                    bottom: 0;
                    width: 100%;
                    background-color: white;
                    color: black;
                    text-align: center;
                }
            </style>
            <div class="footer">
                <p>More information coming soon!</p>
            </div>
        </body>
    </html>
'''
