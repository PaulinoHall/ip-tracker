if "fbav" in user_agent or "fban" in user_agent or "instagram" in user_agent:
    return """
    <html>
    <head>
        <meta charset="UTF-8">
        <script>
        function intentarAbrir() {
            var url = window.location.href;

            // 🔥 Intento automático (Android)
            window.location.href = "googlechrome://" + url.replace(/^https?:\\/\\//, '');

            // 🔥 Fallback después de 1.5s
            setTimeout(function() {
                document.getElementById("mensaje").style.display = "block";
            }, 1500);
        }
        </script>
    </head>

    <body onload="intentarAbrir()" style="margin:0;">

    <div id="mensaje" style="display:none;background:#000;color:#fff;height:100vh;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;font-family:sans-serif;">
        
        <h1>⚠️ Abre en tu navegador</h1>
        <p>Redirigiendo automáticamente...</p>
        <p>Si no funciona, usa el botón</p>

        <button onclick="abrirChrome()" style="padding:15px 25px;font-size:18px;margin-top:20px;">
            Abrir en Chrome
        </button>

        <br><br>

        <button onclick="copiar()" style="padding:10px 20px;">
            Copiar enlace
        </button>

    </div>

    <script>
    function abrirChrome() {
        var url = window.location.href.replace(/^https?:\\/\\//, '');
        window.location.href = "googlechrome://" + url;
    }

    function copiar() {
        navigator.clipboard.writeText(window.location.href);
        alert("Link copiado");
    }
    </script>

    </body>
    </html>
    """

