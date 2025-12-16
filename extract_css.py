import re

def extract_css_from_html(html_file, css_file):
    """
    Extract CSS from HTML file's <style> tag and save to a separate CSS file.
    Updates the HTML to link to the new CSS file.
    """
    # Read the HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Find the style tag and extract CSS content
    style_pattern = r'<style>(.*?)</style>'
    match = re.search(style_pattern, html_content, re.DOTALL)
    
    if not match:
        print("No <style> tag found in HTML file.")
        return
    
    css_content = match.group(1).strip()
    
    # Write CSS to separate file
    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    print(f"✓ CSS extracted to {css_file}")
    
    # Replace <style> tag with <link> to external CSS
    link_tag = f'<link rel="stylesheet" href="{css_file}">'
    updated_html = re.sub(style_pattern, link_tag, html_content, flags=re.DOTALL)
    
    # Write updated HTML back to file
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(updated_html)
    
    print(f"✓ Updated {html_file} to link to external CSS")
    print("\nDone! CSS has been separated successfully.")

if __name__ == "__main__":
    html_file = "index.html"
    css_file = "style.css"
    
    extract_css_from_html(html_file, css_file)
