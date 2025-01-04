from flask import Flask, request, render_template_string, redirect

app = Flask(__name__)

@app.route('/redirect1')
def redirect1():
    encoded_string = request.args.get('JN2FLIX')
    if not encoded_string:
        return "Error: Missing parameter.", 400

    redirect2_url = f"/redirect2?JN2FLIX={encoded_string}"

    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Step 1</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body>
        <h1>Step 1: Get Link</h1>
        <p>Click the button below to proceed.</p>
        <a href="{{ redirect2_url }}">
            <button style="padding: 10px 20px; font-size: 16px;">Get Link</button>
        </a>
    </body>
    </html>
    """
    return render_template_string(html_content, redirect2_url=redirect2_url)

@app.route('/redirect2')
def redirect2():
    encoded_string = request.args.get('JN2FLIX')
    if not encoded_string:
        return "Error: Missing parameter.", 400

    final_link = f"https://jn2flix.blogspot.com/2025/01/file.html?JN2FLIX={encoded_string}"

    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Step 2</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body>
        <h1>Step 2: Final Link</h1>
        <p>Click the button below to access the files.</p>
        <a href="{{ final_link }}">
            <button style="padding: 10px 20px; font-size: 16px;">Final Link</button>
        </a>
    </body>
    </html>
    """
    return render_template_string(html_content, final_link=final_link)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
