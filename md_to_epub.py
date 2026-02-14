import argparse
import os
import markdown
from ebooklib import epub
import uuid

def create_epub_from_markdown(input_dir, output_epub_path):
    book = epub.EpubBook()

    # Set metadata
    book.set_identifier(str(uuid.uuid4()))
    book.set_title(os.path.basename(input_dir).replace('_', ' ').title())
    book.set_language('en')

    book.add_author('ePublisher') # Default author

    chapters = []
    spine = ['nav']
    toc = []

    markdown_files = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(('.md', '.markdown')):
                markdown_files.append(os.path.join(root, file))

    markdown_files.sort() # Ensure consistent order

    for i, md_file in enumerate(markdown_files):
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()

        html_content = markdown.markdown(md_content)

        # Create epub item
        chapter_title = os.path.splitext(os.path.basename(md_file))[0].replace('_', ' ').title()
        
        # Ensure unique file names for chapters within the EPUB
        file_name = f'chap_{i:04d}.xhtml'
        
        c = epub.EpubHtml(title=chapter_title, file_name=file_name, lang='en')
        c.content = f'<h1>{chapter_title}</h1>\\n{html_content}'
        book.add_item(c)
        chapters.append(c)
        spine.append(c)
        toc.append(epub.Section(chapter_title, c))

    # Add default NCX and Nav file
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Define Table Of Contents
    book.toc = toc

    # Define CSS
    style = 'body { font-family: Cambria, Liberation Serif, Bitstream Vera Serif, Georgia, Times, Times New Roman, serif; }'
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)

    # Add the spine
    book.spine = spine

    # Create epub file
    epub.write_epub(output_epub_path, book, {})
    print(f"Successfully created EPUB: {output_epub_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a directory of Markdown files into a single EPUB.")
    parser.add_argument("--input_dir", required=True, help="Path to the directory containing Markdown files.")
    parser.add_argument("--output_epub", required=True, help="Path for the output EPUB file (e.g., my_book.epub).")

    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        print(f"Error: Input directory '{args.input_dir}' does not exist.")
        exit(1)
    
    create_epub_from_markdown(args.input_dir, args.output_epub)
