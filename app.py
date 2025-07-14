from flask import Flask, request, render_template, send_file
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
from urllib.parse import urljoin, urlparse
import io

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None

    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            error = "Te rog introdu un URL valid."
            return render_template('index.html', error=error)

        visited = set()
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)
        base_domain = urlparse(url).netloc

        def crawl(u, depth=0, max_depth=1):
            if u in visited or depth > max_depth:
                return
            visited.add(u)
            try:
                r = requests.get(u, timeout=10)
                soup = BeautifulSoup(r.content, 'html.parser')
                text = soup.get_text(separator='\n', strip=True)
                if text.strip():
                    pdf.add_page()
                    pdf.multi_cell(0, 10, f"URL: {u}\n\n{text[:8000]}")
                for link in soup.find_all('a', href=True):
                    full_url = urljoin(u, link['href'])
                    if base_domain in urlparse(full_url).netloc:
                        crawl(full_url, depth + 1, max_depth)
            except:
                raise RuntimeError("Siteul nu poate fi citit.")

        try:
            crawl(url)
            pdf_output = io.BytesIO()
            pdf.output(pdf_output)
            pdf_output.seek(0)
            return send_file(pdf_output, download_name="site_content.pdf", as_attachment=True)
        except:
            error = "Siteul nu poate fi citit."

    return render_template('index.html', error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
