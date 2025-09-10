import os
import zipfile
import fitz

def extract_images_from_pptx(pptx_path, output_folder="images_pptx"):
    # Make sure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Open pptx as zip (because pptx is just a zip file)
    with zipfile.ZipFile(pptx_path, 'r') as pptx_zip:
        # Loop through all files in pptx
        for file in pptx_zip.namelist():
            # Images are stored under ppt/media/
            if file.startswith("ppt/media/"):
                # Extract image data
                image_data = pptx_zip.read(file)

                # Get the filename (e.g., image1.png, image2.jpeg, etc.)
                image_filename = os.path.basename(file)

                # Save to output folder
                output_path = os.path.join(output_folder, image_filename)
                with open(output_path, "wb") as f:
                    f.write(image_data)

                print(f"Saved: {output_path}")


def extract_images_from_pdf(pdf_path, output_folder="images_pdf"):
    # Make sure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Open PDF
    pdf_doc = fitz.open(pdf_path)

    # Loop through pages
    for page_number in range(len(pdf_doc)):
        page = pdf_doc[page_number]
        images = page.get_images(full=True)

        for img_index, img in enumerate(images, start=1):
            xref = img[0]  # reference id of image
            base_image = pdf_doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]  # usually 'png' or 'jpeg'

            # Build filename
            image_filename = f"page{page_number+1}_img{img_index}.{image_ext}"
            output_path = os.path.join(output_folder, image_filename)

            # Save image
            with open(output_path, "wb") as f:
                f.write(image_bytes)

            print(f"Saved: {output_path}")

    pdf_doc.close()


# Example usage
# extract_images_from_pdf("../../test.pdf", "images_pdf")
# Example usage
# extract_images_from_pptx("test.pptx", "images_pptx")