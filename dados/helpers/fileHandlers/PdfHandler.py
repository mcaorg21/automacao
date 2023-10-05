from PyPDF2 import PdfFileWriter, PdfFileReader
from typing import List

from dados.helpers.Queue import Queue
from dados.helpers.fileHandlers.FileHandler import FileHandler


class PdfHandler:
    def __init__(self, *pdfs: FileHandler):
        self.pdfList: List[FileHandler] = list(pdfs)
        self._pdfQueue: Queue = Queue.from_list(self.pdfList)

    def addPdfToQueue(self, pdf: FileHandler):
        self._pdfQueue.put(pdf)

    def addPdfsToQueue(self, *pdfs: FileHandler):
        self._pdfQueue.extend_from_list(list(pdfs))

    def getPdfFromQueue(self):
        return self._pdfQueue.get()

    def mergePdfsFromQueue(self, output_path) -> FileHandler:
        mergedPdf = FileHandler(path=output_path)

        pdf_writer = PdfFileWriter()
        for pdf in self._pdfQueue:
            pdf_reader = PdfFileReader(pdf.path)
            for page in range(pdf_reader.getNumPages()):
                pdf_writer.addPage(pdf_reader.getPage(page))
        with open(mergedPdf.path, 'wb') as fh:
            pdf_writer.write(fh)

        return mergedPdf

    def __repr__(self):
        return str(self._pdfQueue)
