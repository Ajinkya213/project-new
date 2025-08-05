import os
from typing import List, Dict, Union
import fitz  # PyMuPDF
from PIL import Image
import io

class PdfConverterAlternative:
    '''
    Converts PDF file or PDF files from folder to images using PyMuPDF.
    This is an alternative to the Poppler-based converter.
    '''
    def __init__(self, image_dir=r'..\data\pdf_images'):
        self.saved_images_dir = image_dir
        os.makedirs(self.saved_images_dir, exist_ok=True)
        self._doc_counter = 1
        
    def pdf_to_image(self, file_path: str) -> List[Dict]:
        '''
        Convert a PDF file to images using PyMuPDF.
        
        Args:
            file_path(str): path for the pdf file.
            
        Returns: 
            List[Dict]: List of dictionary with document id, page number, image and filename.
        '''
        pdf_name = os.path.basename(file_path)
        try:
            # Open PDF with PyMuPDF
            doc = fitz.open(file_path)
            print(f"[INFO] Opened PDF: {pdf_name} with {len(doc)} pages")
            
            results = []
            for page_num in range(len(doc)):
                # Get page
                page = doc.load_page(page_num)
                
                # Convert page to image
                mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to PIL Image
                img_data = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_data))
                
                # Save image
                image_filename = f"doc_{self._doc_counter}_page_{page_num+1}_{pdf_name.replace('.pdf', '')}.png"
                image_path = os.path.join(self.saved_images_dir, image_filename)
                image.save(image_path)
                
                results.append({
                    "doc_id": self._doc_counter,
                    "filename": pdf_name,
                    "page_number": page_num+1,
                    "image_path": image_path,
                    "image": image
                })
                
                print(f"[INFO] Processed page {page_num+1}")
            
            doc.close()
            self._doc_counter += 1
            return results
            
        except Exception as e:
            print(f"[ERROR] Failed to convert {pdf_name}: {e}")
            return []
    
    def convert(self, input_path: Union[str, List[str]]) -> List[Dict]:
        '''
        Converts a folder of PDF or a single PDF file into images.
        
        Args:
            input_path (str or List[str]): Path to a PDF file or folder.
        
        Returns:
            List[Dict]: List of image dictionary with metadata
        '''
        all_images = []
        if os.path.isdir(input_path):
            pdf_files = [f for f in os.listdir(input_path) if f.lower().endswith(".pdf")]
            for pdf_file in pdf_files:
                pdf_path = os.path.join(input_path, pdf_file)
                images = self.pdf_to_image(pdf_path)
                all_images.extend(images)
        elif os.path.isfile(input_path) and input_path.lower().endswith(".pdf"):
            all_images = self.pdf_to_image(input_path)
        else:
            raise ValueError(f"[ERROR] Invalid input path: {input_path}")
        return all_images 