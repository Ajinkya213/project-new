import os
from typing import List, Dict, Union
from pdf2image import convert_from_path

class PdfConverter:
    '''
    Converts PDF file or PDF files from folder to images.
    '''
    def __init__(self, image_dir=r'..\data\pdf_images'):
        self.saved_images_dir = image_dir
        os.makedirs(self.saved_images_dir, exist_ok=True)
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        self._doc_counter = 1
        
    def pdf_to_image(self, file_path: str) -> List[Dict]:
        '''
        Convert a PDF file to images.
        
        Args:
            file_path(str): path for the pdf file.
            
        Returns: 
            List[Dict]: List of dictionary with document id, page number, image and filename.
        '''
        pdf_name = os.path.basename(file_path)
        try:
            # Try multiple poppler paths
            poppler_paths = [
                r"C:\Program Files\poppler-24.08.0\Library\bin",
                r"C:\Program Files\poppler\Library\bin",
                r"C:\poppler\bin",
                r"C:\Program Files (x86)\poppler\bin",
                None  # Try without path
            ]
            
            images = None
            for poppler_path in poppler_paths:
                try:
                    if poppler_path:
                        print(f"[INFO] Trying Poppler path: {poppler_path}")
                        images = convert_from_path(file_path, poppler_path=poppler_path)
                        print(f"[INFO] Successfully converted with Poppler path: {poppler_path}")
                        break
                    else:
                        print("[INFO] Trying default Poppler path")
                        images = convert_from_path(file_path)
                        print("[INFO] Successfully converted with default path")
                        break
                except Exception as e:
                    print(f"[WARNING] Failed with path {poppler_path}: {e}")
                    continue
            
            if images is None:
                raise Exception("All Poppler paths failed")
                
        except Exception as e:
            print(f"[ERROR] Failed to convert {pdf_name}: {e}")
            return []
        
        results = []
        for page_num, image in enumerate(images):
            image_filename = f"doc_{self._doc_counter}_page_{page_num+1}_{pdf_name.replace('.pdf', '')}.png"
            image_path = os.path.join(self.saved_images_dir, image_filename)
            image.convert('RGB').save(image_path)
            
            results.append({
                "doc_id": self._doc_counter,
                "filename": pdf_name,
                "page_number": page_num+1,
                "image_path": image_path,
                "image": image.convert('RGB')
            })
        self._doc_counter += 1
        return results
    
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