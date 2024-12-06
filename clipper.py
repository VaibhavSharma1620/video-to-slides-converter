import os
import sys
import time
import cv2
import shutil
import img2pdf
import glob
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import imagehash
import pytesseract
from fpdf import FPDF
from datetime import datetime
import json
from skimage.metrics import structural_similarity as ssim
import threading
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class VideoProcessor:
    def __init__(self):
        # Background subtraction parameters
        self.FRAME_BUFFER_HISTORY = 15
        self.DEC_THRESH = 0.75
        self.DIST_THRESH = 100
        self.MIN_PERCENT = 0.15
        self.MAX_PERCENT = 0.01
        
        # Frame differencing parameters
        self.MIN_PERCENT_THRESH = 0.06
        self.ELAPSED_FRAME_THRESH = 85
        
        self.recognized_text = {}
        self.timestamps = {}
        self.ocr=False
        
        self.processing = False
        self.current_progress = 0
    
    def resize_frame(self, frame, resize_width=640):
        ht, wd, _ = frame.shape
        new_height = resize_width * ht / wd
        return cv2.resize(frame, (resize_width, int(new_height)), interpolation=cv2.INTER_AREA)
    
    def create_output_dir(self, video_path, output_path, method):
        vid_file_name = os.path.basename(video_path).split('.')[0]
        output_dir_path = os.path.join(output_path, vid_file_name, method)
        
        if os.path.exists(output_dir_path):
            shutil.rmtree(output_dir_path)
        os.makedirs(output_dir_path, exist_ok=True)
        return output_dir_path

    def extract_text_from_frame(self, frame):
        """Extract text from frame using OCR"""
        try:
            # Convert frame to PIL Image
            pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            # Extract text using pytesseract
            text = pytesseract.image_to_string(pil_image)
            return text.strip()
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""
    
    def generate_smart_summary(self, output_dir):
        """Generate a summary report with extracted information"""
        summary = {
            'total_slides': len(glob.glob(os.path.join(output_dir, "*.png"))),
            'text_content': self.recognized_text,
            'timestamps': self.timestamps,
            'processing_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Save summary as JSON
        with open(os.path.join(output_dir, 'summary.json'), 'w') as f:
            json.dump(summary, f, indent=4)
        
        # Generate PDF report
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Add summary information
        pdf.cell(200, 10, txt="Video Analysis Summary", ln=True, align='C')
        pdf.cell(200, 10, txt=f"Total Slides: {summary['total_slides']}", ln=True)
        
        # Add timestamps
        pdf.cell(200, 10, txt="Slide Timestamps:", ln=True)
        for slide, timestamp in summary['timestamps'].items():
            pdf.cell(200, 10, txt=f"Slide {slide}: {timestamp}", ln=True)
        
        pdf.output(os.path.join(output_dir, "analysis_report.pdf"))
    
    def process_video_knn(self, video_path, output_dir, progress_callback=None):
        bg_sub = cv2.createBackgroundSubtractorKNN(
            history=self.FRAME_BUFFER_HISTORY,
            dist2Threshold=self.DIST_THRESH,
            detectShadows=False
        )
        
        screenshots_count = 0
        capture_frame = False
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        while cap.isOpened() and self.processing:
            ret, frame = cap.read()
            if not ret:
                break
            current_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
            self.current_progress = int((cap.get(cv2.CAP_PROP_POS_FRAMES) / total_frames) * 100)
            if progress_callback:
                progress_callback(self.current_progress)
            
            orig_frame = frame.copy()
            frame = self.resize_frame(frame)
            fg_mask = bg_sub.apply(frame)
            p_non_zero = (cv2.countNonZero(fg_mask) / fg_mask.size) * 100
            
            if p_non_zero < self.MAX_PERCENT and not capture_frame:
                
                capture_frame = True
                screenshots_count += 1
                filename = f"{screenshots_count:03d}.png"
                if self.ocr==True:
                    text = self.extract_text_from_frame(frame)   
                    self.recognized_text[filename] = text
                self.timestamps[filename] = time.strftime('%H:%M:%S', time.gmtime(current_frame/fps))

                cv2.imwrite(os.path.join(output_dir, filename), orig_frame)
            elif p_non_zero >= self.MIN_PERCENT:
                capture_frame = False
        
        cap.release()
        return screenshots_count

    def process_video_gmg(self, video_path, output_dir, progress_callback=None):
        bg_sub = cv2.bgsegm.createBackgroundSubtractorGMG(
            initializationFrames=self.FRAME_BUFFER_HISTORY,
            decisionThreshold=self.DEC_THRESH
        )
        screenshots_count = 0
        capture_frame = False
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        while cap.isOpened() and self.processing:
            ret, frame = cap.read()
            if not ret:
                break
            current_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
            self.current_progress = int((cap.get(cv2.CAP_PROP_POS_FRAMES) / total_frames) * 100)
            if progress_callback:
                progress_callback(self.current_progress)
            
            orig_frame = frame.copy()
            frame = self.resize_frame(frame)
            fg_mask = bg_sub.apply(frame)
            p_non_zero = (cv2.countNonZero(fg_mask) / fg_mask.size) * 100
            
            if p_non_zero < self.MAX_PERCENT and not capture_frame:
                
                capture_frame = True
                screenshots_count += 1
                filename = f"{screenshots_count:03d}.png"
                if self.ocr==True:
                    text = self.extract_text_from_frame(frame)   
                    print('text = ',text )
                    self.recognized_text[filename] = text
                self.timestamps[filename] = time.strftime('%H:%M:%S', time.gmtime(current_frame/fps))

                cv2.imwrite(os.path.join(output_dir, filename), orig_frame)
            elif p_non_zero >= self.MIN_PERCENT:
                capture_frame = False
        
        cap.release()
        return screenshots_count

        

    def process_frame_diff(self, video_path, output_dir, progress_callback=None):
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7,7))
        prev_frame = None
        screenshots_count = 0
        capture_frame = False
        frame_elapsed = 0
        
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        while cap.isOpened() and self.processing:
            ret, frame = cap.read()
            if not ret:
                break
            current_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
            self.current_progress = int((cap.get(cv2.CAP_PROP_POS_FRAMES) / total_frames) * 100)
            if progress_callback:
                progress_callback(self.current_progress)
            
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if prev_frame is not None:
                frame_diff = cv2.absdiff(frame_gray, prev_frame)
                _, frame_diff = cv2.threshold(frame_diff, 80, 255, cv2.THRESH_BINARY)
                frame_diff = cv2.dilate(frame_diff, kernel)
                
                p_non_zero = (cv2.countNonZero(frame_diff) / frame_gray.size) * 100
                
                if p_non_zero >= self.MIN_PERCENT_THRESH and not capture_frame:
                    capture_frame = True
                elif capture_frame:
                    frame_elapsed += 1
                
                if frame_elapsed >= self.ELAPSED_FRAME_THRESH:
                    capture_frame = False
                    frame_elapsed = 0
                    screenshots_count += 1
                    filename = f"{screenshots_count:03d}.png"
                    if self.ocr==True:
                        text = self.extract_text_from_frame(frame)   
                        self.recognized_text[filename] = text
                    self.timestamps[filename] = time.strftime('%H:%M:%S', time.gmtime(current_frame/fps))

                    cv2.imwrite(os.path.join(output_dir, filename), frame)
            
            prev_frame = frame_gray
        
        cap.release()
        return screenshots_count

class DuplicateRemover:
    @staticmethod
    def compare_images(img1, img2):
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        
        return ssim(gray1, gray2, full=True)[0]

    @staticmethod
    def remove_duplicates(directory, similarity_threshold=0.98):
        files = sorted(glob.glob(os.path.join(directory, "*.png")))
        duplicates = []
        
        for i in range(1, len(files)):
            img1 = cv2.imread(files[i-1])
            img2 = cv2.imread(files[i])
            print(i,DuplicateRemover.compare_images(img1, img2))
            if DuplicateRemover.compare_images(img1, img2) >= similarity_threshold:
                duplicates.append(files[i])
        
        for file in duplicates:
            os.remove(file)
        
        return len(duplicates)

class VideoToSlidesGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Video to Slides Converter")
        self.root.geometry("800x600")
        
        self.video_processor = VideoProcessor()
        self.setup_gui()
    
    def setup_gui(self):
        # Input frame
        input_frame = ttk.LabelFrame(self.root, text="Input", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.video_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.generate_report = tk.BooleanVar(value=True)
        self.Ocr = tk.BooleanVar(value=True)
        ttk.Entry(input_frame, textvariable=self.video_path, width=50).pack(side=tk.LEFT)
        ttk.Button(input_frame, text="Browse", command=self.browse_video).pack(side=tk.LEFT, padx=5)
        
        # Output frame
        output_frame = ttk.LabelFrame(self.root, text="Output", padding=10)
        output_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Entry(output_frame, textvariable=self.output_path, width=50).pack(side=tk.LEFT)
        ttk.Button(output_frame, text="Browse", command=self.browse_output).pack(side=tk.LEFT, padx=5)
        
        # Options frame
        options_frame = ttk.LabelFrame(self.root, text="Options", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.method = tk.StringVar(value="KNN")
        ttk.Radiobutton(options_frame, text="KNN", variable=self.method, value="KNN").pack(side=tk.LEFT)
        ttk.Radiobutton(options_frame, text="GMG", variable=self.method, value="GMG").pack(side=tk.LEFT)
        ttk.Radiobutton(options_frame, text="Frame Diff", variable=self.method, value="Frame_Diff").pack(side=tk.LEFT)
        
        self.remove_duplicates = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Remove Duplicates", variable=self.remove_duplicates).pack(side=tk.LEFT)
        
        self.convert_pdf = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Convert to PDF", variable=self.convert_pdf).pack(side=tk.LEFT)
        ttk.Checkbutton(options_frame, text="Generate Report", variable=self.generate_report).pack(side=tk.LEFT)
        ttk.Checkbutton(options_frame, text="OCR", variable=self.Ocr).pack(side=tk.LEFT)

        # Progress frame
        progress_frame = ttk.LabelFrame(self.root, text="Progress", padding=10)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress = ttk.Progressbar(progress_frame, length=400, mode='determinate')
        self.progress.pack(fill=tk.X)
        
        # Control buttons
        button_frame = ttk.Frame(self.root, padding=10)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_processing)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_processing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
    
    def browse_video(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Video files", "*.mp4 *.avi *.mkv"), ("All files", "*.*")]
        )
        if filename:
            self.video_path.set(filename)
    
    def browse_output(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_path.set(directory)
    
    def update_progress(self, value):
        self.progress['value'] = value
        self.root.update_idletasks()
    
    def start_processing(self):
        if not self.video_path.get() or not self.output_path.get():
            messagebox.showerror("Error", "Please select both input video and output directory")
            return
        
        self.video_processor.processing = True
        self.start_button['state'] = tk.DISABLED
        self.stop_button['state'] = tk.NORMAL
        
        threading.Thread(target=self.process_video, daemon=True).start()
    
    def stop_processing(self):
        self.video_processor.processing = False
        self.start_button['state'] = tk.NORMAL
        self.stop_button['state'] = tk.DISABLED
    
    def process_video(self):
        try:
            output_dir = self.video_processor.create_output_dir(
                self.video_path.get(),
                self.output_path.get(),
                self.method.get()
            )
            if self.Ocr.get():
                self.video_processor.ocr=True
            if self.method.get() == "KNN":
                self.video_processor.process_video_knn(
                    self.video_path.get(),
                    output_dir,
                    self.update_progress
                )
            elif self.method.get() == "GMG":
                self.video_processor.process_video_gmg(
                    self.video_path.get(),
                    output_dir,
                    self.update_progress
                )
            else:
                self.video_processor.process_frame_diff(
                    self.video_path.get(),
                    output_dir,
                    self.update_progress
                )
            
            if self.remove_duplicates.get():
                DuplicateRemover.remove_duplicates(output_dir)
            
            if self.generate_report.get():
                self.video_processor.generate_smart_summary(output_dir)
            
            

            if self.convert_pdf.get():
                pdf_path = os.path.join(output_dir, f"{os.path.basename(self.video_path.get())}.pdf")
                with open(pdf_path, "wb") as f:
                    f.write(img2pdf.convert(sorted(glob.glob(os.path.join(output_dir, "*.png")))))
            
            messagebox.showinfo("Success", "Processing completed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            self.stop_processing()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = VideoToSlidesGUI()
    app.run()