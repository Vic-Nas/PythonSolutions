"""
PDF Compactor GUI Module
Generated with Claude AI assistance

Graphical user interface for PDF compaction using tkinter.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, Canvas, Listbox, MULTIPLE, colorchooser
from tkinter import ttk, StringVar, IntVar, BooleanVar
from PIL import Image, ImageTk
import platform
import tempfile
import fitz

import math
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Optional, Union


# A4 dimensions in points (1 point = 1/72 inch)
A4_WIDTH = 595.276  # 210mm
A4_HEIGHT = 841.890  # 297mm


class LayoutMode(Enum):
    """Layout mode for PDF compaction."""
    GRID = "grid"  # Manual rows × columns
    TARGET_PAGES = "target_pages"  # Auto-calculate grid from target page count


class PageOrder(Enum):
    """Order in which pages are placed on the grid."""
    HORIZONTAL = "horizontal"  # Fill left-to-right, then top-to-bottom
    VERTICAL = "vertical"  # Fill top-to-bottom, then left-to-right


@dataclass
class CompactionConfig:
    """
    Configuration for PDF compaction.
    
    Attributes:
        rows: Number of rows per output page (grid mode)
        columns: Number of columns per output page (grid mode)
        targetPages: Target number of output pages (target_pages mode)
        layoutMode: Layout mode to use (GRID or TARGET_PAGES)
        compression: Image quality percentage (25-100, where 100=original)
        separationPages: Number of blank pages to insert between input PDFs
        pageOrder: Order for placing pages (HORIZONTAL or VERTICAL)
        maintainAspectRatio: Whether to maintain aspect ratio when scaling
        showGrid: Whether to draw grid lines on output pages
        gridColor: RGB tuple for grid color (0-1 range for each component)
        addPageNumbers: Whether to add page numbers to each cell
        outputDir: Directory for output file (None = auto-create VicOutput)
        outputFilename: Name of output file (None = auto-generate)
    """
    rows: int = 1
    columns: int = 1
    targetPages: int = 1
    layoutMode: LayoutMode = LayoutMode.GRID
    compression: int = 100
    separationPages: int = 0
    pageOrder: PageOrder = PageOrder.HORIZONTAL
    maintainAspectRatio: bool = True
    showGrid: bool = False
    gridColor: Tuple[float, float, float] = (0, 0, 0)
    addPageNumbers: bool = False
    outputDir: Optional[str] = None
    outputFilename: Optional[str] = None
    
    def __post_init__(self):
        """Validate configuration values."""
        self.compression = max(25, min(100, self.compression))
        self.rows = max(1, self.rows)
        self.columns = max(1, self.columns)
        self.targetPages = max(1, self.targetPages)
        self.separationPages = max(0, self.separationPages)


def calculateOptimalGrid(totalPages: int, targetPages: int) -> Tuple[int, int]:
    """
    Calculate optimal grid (rows × columns) for given target page count.
    
    Attempts to create a grid as close to square as possible while fitting
    all pages within the target number of output pages.
    
    Args:
        totalPages: Total number of input pages to distribute
        targetPages: Desired number of output pages
        
    Returns:
        Tuple of (rows, columns) for the grid
        
    Example:
        >>> calculateOptimalGrid(24, 3)
        (2, 4)  # 2×4 grid = 8 pages per output, 24/8 = 3 output pages
    """
    if targetPages <= 0 or totalPages <= 0:
        return 1, 1
    
    # Calculate pages per output page
    pagesPerOutput = math.ceil(totalPages / targetPages)
    
    # Find factors closest to square root for most balanced grid
    sqrtVal = math.sqrt(pagesPerOutput)
    bestRows = 1
    bestCols = pagesPerOutput
    minDiff = abs(bestRows - bestCols)
    
    # Try to find perfect factors
    for rows in range(1, int(sqrtVal) + 2):
        if pagesPerOutput % rows == 0:
            cols = pagesPerOutput // rows
            diff = abs(rows - cols)
            if diff < minDiff:
                minDiff = diff
                bestRows = rows
                bestCols = cols
    
    # If no perfect factors, find closest approximation
    if bestRows * bestCols != pagesPerOutput:
        bestRows = int(sqrtVal)
        bestCols = math.ceil(pagesPerOutput / bestRows)
    
    return bestRows, bestCols


def _countTotalPages(pdfPaths: List[str], separationPages: int = 0) -> int:
    """
    Count total pages across all PDFs including separation pages.
    
    Args:
        pdfPaths: List of PDF file paths
        separationPages: Number of blank pages between PDFs
        
    Returns:
        Total page count
    """
    totalPages = 0
    for pdfPath in pdfPaths:
        doc = fitz.open(pdfPath)
        totalPages += len(doc)
        doc.close()
    
    # Add separation pages (n-1 separations for n PDFs)
    if len(pdfPaths) > 1:
        totalPages += (len(pdfPaths) - 1) * separationPages
    
    return totalPages


def _getLayoutParameters(
    config: CompactionConfig,
    pdfPaths: List[str]
) -> Tuple[int, int]:
    """
    Determine rows and columns based on layout mode.
    
    Args:
        config: Compaction configuration
        pdfPaths: List of input PDF paths
        
    Returns:
        Tuple of (rows, columns)
    """
    if config.layoutMode == LayoutMode.GRID:
        return config.rows, config.columns
    else:  # TARGET_PAGES mode
        totalPages = _countTotalPages(pdfPaths, config.separationPages)
        return calculateOptimalGrid(totalPages, config.targetPages)


def mergePdfPages(
    docs: List[fitz.Document],
    compression: int,
    separationPages: int = 0
) -> List[Optional[fitz.Pixmap]]:
    """
    Merge and compress pages from multiple PDF documents.
    
    Args:
        docs: List of opened fitz.Document objects
        compression: Compression percentage (25-100)
        separationPages: Number of blank pages to insert between documents
        
    Returns:
        List of fitz.Pixmap objects (or None for blank separation pages)
    """
    allPages = []
    compression = max(25, min(100, compression))
    
    for docIdx, doc in enumerate(docs):
        for pageNum in range(len(doc)):
            page = doc[pageNum]
            
            # Use compression factor for rendering
            zoom = compression / 100.0
            matrix = fitz.Matrix(zoom, zoom)
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            
            # Convert to RGB if needed (remove alpha channel)
            if pixmap.alpha:
                pixmap = fitz.Pixmap(fitz.csRGB, pixmap)
            
            allPages.append(pixmap)
        
        # Add separation pages between documents
        if docIdx < len(docs) - 1 and separationPages > 0:
            for _ in range(separationPages):
                allPages.append(None)
    
    return allPages


def _placePageOnGrid(
    newPage: fitz.Page,
    pixmap: fitz.Pixmap,
    index: int,
    columns: int,
    rows: int,
    cellWidth: float,
    cellHeight: float,
    pageOrder: PageOrder,
    maintainAspectRatio: bool,
    addPageNumbers: bool
) -> None:
    """
    Place a page pixmap on the grid at the specified position.
    
    Args:
        newPage: The output page to draw on
        pixmap: The page image to place
        index: Linear index of the page in the grid
        columns: Number of columns in the grid
        rows: Number of rows in the grid
        cellWidth: Width of each grid cell
        cellHeight: Height of each grid cell
        pageOrder: Order for placing pages (HORIZONTAL or VERTICAL)
        maintainAspectRatio: Whether to maintain aspect ratio
        addPageNumbers: Whether to add page numbers
    """
    # Calculate grid position based on page order
    if pageOrder == PageOrder.HORIZONTAL:
        xOffset = (index % columns) * cellWidth
        yOffset = (index // columns) * cellHeight
    else:  # VERTICAL
        xOffset = (index // rows) * cellWidth
        yOffset = (index % rows) * cellHeight
    
    # Calculate image rectangle
    if maintainAspectRatio:
        aspect = pixmap.width / pixmap.height
        cellAspect = cellWidth / cellHeight
        
        if aspect > cellAspect:
            # Width-constrained
            newWidth = cellWidth
            newHeight = cellWidth / aspect
            yOffset += (cellHeight - newHeight) / 2
        else:
            # Height-constrained
            newHeight = cellHeight
            newWidth = cellHeight * aspect
            xOffset += (cellWidth - newWidth) / 2
        
        imgRect = fitz.Rect(xOffset, yOffset, xOffset + newWidth, yOffset + newHeight)
    else:
        # Fill entire cell
        imgRect = fitz.Rect(xOffset, yOffset, xOffset + cellWidth, yOffset + cellHeight)
    
    newPage.insert_image(imgRect, pixmap=pixmap)
    
    # Add page number if requested
    if addPageNumbers:
        text = str(index + 1)
        textRect = fitz.Rect(xOffset + 5, yOffset + 5, xOffset + 30, yOffset + 20)
        newPage.insert_textbox(textRect, text, fontsize=10, color=(1, 0, 0))


def _drawGrid(
    page: fitz.Page,
    columns: int,
    rows: int,
    cellWidth: float,
    cellHeight: float,
    gridColor: Tuple[float, float, float]
) -> None:
    """
    Draw grid lines on the output page.
    
    Args:
        page: The page to draw on
        columns: Number of columns
        rows: Number of rows
        cellWidth: Width of each cell
        cellHeight: Height of each cell
        gridColor: RGB color tuple (0-1 range)
    """
    # Draw vertical lines
    for x in range(1, columns):
        page.draw_line(
            fitz.Point(x * cellWidth, 0),
            fitz.Point(x * cellWidth, A4_HEIGHT),
            color=gridColor
        )
    
    # Draw horizontal lines
    for y in range(1, rows):
        page.draw_line(
            fitz.Point(0, y * cellHeight),
            fitz.Point(A4_WIDTH, y * cellHeight),
            color=gridColor
        )


def compactPdfs(
    inputPdfPaths: Union[str, List[str]],
    config: Optional[CompactionConfig] = None
) -> str:
    """
    Compact multiple PDF pages onto single A4 pages in a grid layout.
    
    This is the main function for programmatic PDF compaction. It takes one or
    more input PDFs and creates a single output PDF with pages arranged in a grid.
    
    Args:
        inputPdfPaths: Single PDF path or list of PDF paths to compact
        config: CompactionConfig object (uses defaults if None)
        
    Returns:
        Path to the created output PDF file
        
    Raises:
        FileNotFoundError: If any input PDF doesn't exist
        ValueError: If inputPdfPaths is empty
        
    Example:
        >>> from vicutils.pdf import compactPdfs, CompactionConfig, LayoutMode
        >>> 
        >>> # Simple 2×2 grid
        >>> output = compactPdfs("input.pdf", CompactionConfig(rows=2, columns=2))
        >>> 
        >>> # Auto-calculate grid for 5 output pages
        >>> config = CompactionConfig(
        ...     layoutMode=LayoutMode.TARGET_PAGES,
        ...     targetPages=5,
        ...     compression=85,
        ...     showGrid=True
        ... )
        >>> output = compactPdfs(["file1.pdf", "file2.pdf"], config)
    """
    # Handle single path input
    if isinstance(inputPdfPaths, str):
        inputPdfPaths = [inputPdfPaths]
    
    if not inputPdfPaths:
        raise ValueError("No input PDF paths provided")
    
    # Validate all input files exist
    for path in inputPdfPaths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"PDF not found: {path}")
    
    # Use default config if none provided
    if config is None:
        config = CompactionConfig()
    
    # Determine layout parameters
    rows, columns = _getLayoutParameters(config, inputPdfPaths)
    cellWidth = A4_WIDTH / columns
    cellHeight = A4_HEIGHT / rows
    
    # Determine output path
    if config.outputDir:
        outputDir = config.outputDir
    else:
        outputDir = os.path.join(os.path.dirname(inputPdfPaths[0]), "VicOutput")
    os.makedirs(outputDir, exist_ok=True)
    
    if config.outputFilename:
        filename = config.outputFilename
        if not filename.endswith('.pdf'):
            filename += '.pdf'
    else:
        filename = "vicOutput.pdf"
    
    outputPath = os.path.join(outputDir, filename)
    
    # Open all input PDFs
    docs = [fitz.open(path) for path in inputPdfPaths]
    
    try:
        # Merge and compress all pages
        allPages = mergePdfPages(docs, config.compression, config.separationPages)
        
        # Create output document
        outputDoc = fitz.open()
        pagesPerOutput = rows * columns
        
        # Process pages in groups
        for i in range(0, len(allPages), pagesPerOutput):
            # Create new A4 page
            newPage = outputDoc.new_page(width=A4_WIDTH, height=A4_HEIGHT)
            pageGroup = allPages[i:i + pagesPerOutput]
            
            # Place each page in the group
            for idx, pixmap in enumerate(pageGroup):
                if pixmap is not None:  # Skip separation pages
                    _placePageOnGrid(
                        newPage,
                        pixmap,
                        idx,
                        columns,
                        rows,
                        cellWidth,
                        cellHeight,
                        config.pageOrder,
                        config.maintainAspectRatio,
                        config.addPageNumbers
                    )
            
            # Draw grid if requested
            if config.showGrid:
                _drawGrid(newPage, columns, rows, cellWidth, cellHeight, config.gridColor)
        
        # Save with compression
        outputDoc.save(
            outputPath,
            garbage=4,  # Maximum garbage collection
            deflate=True,  # Compress content streams
            clean=True  # Clean and optimize
        )
        outputDoc.close()
        
    finally:
        # Clean up input documents
        for doc in docs:
            doc.close()
    
    return outputPath

# Language translations
TRANSLATIONS = {
    'en': {
        'title': "PDF Compactor",
        'input_files': "📁 Input Files",
        'add_pdfs': "➕ Add PDFs",
        'remove': "🗑️ Remove",
        'move_up': "↑ Move Up",
        'move_down': "↓ Move Down",
        'clear_all': "🗑️ Clear All",
        'layout_params': "⚙️ Layout Parameters",
        'layout_mode': "Layout Mode:",
        'grid_mode': "Grid (Rows × Columns)",
        'target_pages_mode': "Target Pages",
        'rows': "Rows (p):",
        'columns': "Columns (n):",
        'target_pages': "Target Pages:",
        'compression': "Compression (%):",
        'separation': "Separation (pages):",
        'advanced_options': "🔧 Advanced Options",
        'page_order': "Page Order:",
        'horizontal': "Horizontal",
        'vertical': "Vertical",
        'quality_preset': "Quality Preset:",
        'low': "Low",
        'medium': "Medium",
        'high': "High",
        'maximum': "Maximum",
        'grid': "Grid:",
        'show': "Show",
        'hide': "Hide",
        'choose_color': "Choose Color",
        'maintain_aspect': "Maintain aspect ratio",
        'add_page_numbers': "Add page numbers",
        'output_options': "💾 Output Options",
        'folder': "Folder:",
        'filename': "Filename:",
        'browse': "📂 Browse",
        'preview': "👁️ Preview",
        'create_pdf': "✅ Create PDF",
        'ready': "Ready",
        'confirm': "Confirm",
        'clear_all_confirm': "Clear all files?",
        'error': "Error",
        'success': "Success",
        'no_files_error': "Please add at least one PDF file",
        'preview_failed': "Failed to generate preview",
        'pdf_failed': "Failed to create PDF",
        'pdf_created': "PDF created successfully!",
        'saved_to': "Saved to:",
        'added_files': "Added {0} file(s)",
        'removed_files': "Removed selected files",
        'cleared_files': "Cleared all files",
        'preview_generating': "Generating preview...",
        'preview_success': "Preview generated successfully",
        'creating_pdf': "Creating PDF...",
        'pdf_saved': "PDF saved: {0}",
        'default_folder': "Default: VicOutput in source folder",
        'default_filename': "Default: vicOutput.pdf",
        'preview_title': "PDF Preview",
        'language': "Language:",
        'calculated_grid': "Calculated grid: {0}×{1}"
    },
    'fr': {
        'title': "Compacteur PDF",
        'input_files': "📁 Fichiers d'entrée",
        'add_pdfs': "➕ Ajouter PDFs",
        'remove': "🗑️ Supprimer",
        'move_up': "↑ Monter",
        'move_down': "↓ Descendre",
        'clear_all': "🗑️ Tout effacer",
        'layout_params': "⚙️ Paramètres de mise en page",
        'layout_mode': "Mode de mise en page:",
        'grid_mode': "Grille (Rangées × Colonnes)",
        'target_pages_mode': "Pages cibles",
        'rows': "Rangées (p):",
        'columns': "Colonnes (n):",
        'target_pages': "Pages cibles:",
        'compression': "Compression (%):",
        'separation': "Séparation (pages):",
        'advanced_options': "🔧 Options avancées",
        'page_order': "Ordre des pages:",
        'horizontal': "Horizontal",
        'vertical': "Vertical",
        'quality_preset': "Préréglage qualité:",
        'low': "Basse",
        'medium': "Moyenne",
        'high': "Haute",
        'maximum': "Maximum",
        'grid': "Grille:",
        'show': "Afficher",
        'hide': "Masquer",
        'choose_color': "Choisir couleur",
        'maintain_aspect': "Maintenir le ratio d'aspect",
        'add_page_numbers': "Ajouter numéros de page",
        'output_options': "💾 Options de sortie",
        'folder': "Dossier:",
        'filename': "Nom du fichier:",
        'browse': "📂 Parcourir",
        'preview': "👁️ Aperçu",
        'create_pdf': "✅ Créer PDF",
        'ready': "Prêt",
        'confirm': "Confirmer",
        'clear_all_confirm': "Effacer tous les fichiers?",
        'error': "Erreur",
        'success': "Succès",
        'no_files_error': "Veuillez ajouter au moins un fichier PDF",
        'preview_failed': "Échec de génération de l'aperçu",
        'pdf_failed': "Échec de création du PDF",
        'pdf_created': "PDF créé avec succès!",
        'saved_to': "Enregistré dans:",
        'added_files': "{0} fichier(s) ajouté(s)",
        'removed_files': "Fichiers sélectionnés supprimés",
        'cleared_files': "Tous les fichiers effacés",
        'preview_generating': "Génération de l'aperçu...",
        'preview_success': "Aperçu généré avec succès",
        'creating_pdf': "Création du PDF...",
        'pdf_saved': "PDF enregistré: {0}",
        'default_folder': "Par défaut: VicOutput dans le dossier source",
        'default_filename': "Par défaut: vicOutput.pdf",
        'preview_title': "Aperçu PDF",
        'language': "Langue:",
        'calculated_grid': "Grille calculée: {0}×{1}"
    }
}


class PdfCompactorApp:
    """Main application class for PDF Compactor GUI."""
    
    def __init__(self, root):
        """
        Initialize the PDF Compactor application.
        
        Args:
            root: tkinter root window
        """
        self.root = root
        self.currentLanguage = 'en'
        self._setupWindow()
        self._setupVariables()
        self._setupUi()
        
    def _setupWindow(self):
        """Configure window based on platform."""
        # Set window size
        windowWidth = 700
        windowHeight = 700
        
        # Center window on screen
        screenWidth = self.root.winfo_screenwidth()
        screenHeight = self.root.winfo_screenheight()
        x = (screenWidth - windowWidth) // 2
        y = (screenHeight - windowHeight) // 2
        
        self.root.geometry(f"{windowWidth}x{windowHeight}+{x}+{y}")
        self.root.configure(bg="#2C3E50")
        
        # Allow window resizing
        self.root.minsize(650, 650)
        
        # Platform-specific font configurations
        system = platform.system()
        if system == "Darwin":  # macOS
            try:
                self.root.option_add("*Font", ("SF Pro", 12))
            except:
                self.root.option_add("*Font", ("Helvetica", 12))
        elif system == "Windows":
            try:
                self.root.option_add("*Font", ("Segoe UI", 10))
            except:
                self.root.option_add("*Font", ("Arial", 10))
        else:  # Linux
            try:
                self.root.option_add("*Font", ("Ubuntu", 10))
            except:
                self.root.option_add("*Font", ("Sans", 10))
        
        self.root.title(self._translate('title'))
            
    def _setupVariables(self):
        """Initialize all tkinter variables."""
        self.gridOption = StringVar(value=self._translate('show'))
        self.gridColor = StringVar(value="#000000")
        self.outputFolder = StringVar()
        self.pdfName = StringVar()
        self.pageOrder = StringVar(value=self._translate('horizontal'))
        self.maintainAspect = BooleanVar(value=True)
        self.addPageNumbers = BooleanVar(value=False)
        self.quality = StringVar(value=self._translate('high'))
        self.languageVar = StringVar(value='en')
        self.layoutMode = StringVar(value='grid')
        
        # Numeric values
        self.rows = IntVar(value=1)
        self.cols = IntVar(value=1)
        self.separation = IntVar(value=0)
        self.targetPages = IntVar(value=1)
        
    def _translate(self, key):
        """
        Translate key to current language.
        
        Args:
            key: Translation key
            
        Returns:
            Translated string
        """
        return TRANSLATIONS.get(self.currentLanguage, TRANSLATIONS['en']).get(key, key)
        
    def _changeLanguage(self, event=None):
        """Change application language and rebuild UI."""
        self.currentLanguage = self.languageVar.get()
        savedFiles = list(self.listboxFiles.get(0, tk.END))
        
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self._setupUi()
        
        for file in savedFiles:
            self.listboxFiles.insert(tk.END, file)
        
        self.root.title(self._translate('title'))
        
    def _setupUi(self):
        """Create the complete user interface."""
        # Main container with scrollbar
        mainContainer = tk.Frame(self.root, bg="#2C3E50")
        mainContainer.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas and scrollbar
        canvas = tk.Canvas(mainContainer, bg="#2C3E50", highlightthickness=0)
        scrollbar = tk.Scrollbar(mainContainer, orient="vertical", command=canvas.yview)
        scrollableFrame = tk.Frame(canvas, bg="#2C3E50")
        
        scrollableFrame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvasWindow = canvas.create_window((0, 0), window=scrollableFrame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Center content
        def centerContent(event):
            canvas.itemconfig(canvasWindow, width=event.width)
        canvas.bind('<Configure>', centerContent)
        
        # Mouse wheel scrolling
        def onMousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", onMousewheel)
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Build UI sections
        self._createHeader(scrollableFrame)
        self._createFilesSection(scrollableFrame)
        self._createBasicParamsSection(scrollableFrame)
        self._createAdvancedOptionsSection(scrollableFrame)
        self._createOutputSection(scrollableFrame)
        self._createActionButtons(scrollableFrame)
        self._createStatusBar()
        
    def _createHeader(self, parent):
        """Create title and language selector."""
        headerFrame = tk.Frame(parent, bg="#2C3E50")
        headerFrame.pack(fill=tk.X, pady=(0, 10))
        
        titleLabel = tk.Label(
            headerFrame,
            text=self._translate('title'),
            font=("Arial", 18, "bold"),
            bg="#2C3E50",
            fg="white"
        )
        titleLabel.pack(side=tk.LEFT, padx=(0, 20))
        
        langFrame = tk.Frame(headerFrame, bg="#2C3E50")
        langFrame.pack(side=tk.RIGHT)
        
        tk.Label(
            langFrame,
            text=self._translate('language'),
            bg="#2C3E50",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        langMenu = ttk.Combobox(
            langFrame,
            textvariable=self.languageVar,
            values=['en', 'fr'],
            state="readonly",
            width=8
        )
        langMenu.set(self.currentLanguage)
        langMenu.pack(side=tk.LEFT)
        langMenu.bind("<<ComboboxSelected>>", self._changeLanguage)
        
    def _createFilesSection(self, parent):
        """Create file selection section."""
        filesFrame = tk.LabelFrame(
            parent,
            text=self._translate('input_files'),
            bg="#34495E",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=10
        )
        filesFrame.pack(fill=tk.BOTH, expand=False, pady=5)
        
        # Listbox with scrollbar
        listContainer = tk.Frame(filesFrame, bg="#34495E")
        listContainer.pack(fill=tk.BOTH, expand=False)
        
        scrollbar = tk.Scrollbar(listContainer)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listboxFiles = Listbox(
            listContainer,
            selectmode=MULTIPLE,
            height=4,
            yscrollcommand=scrollbar.set,
            bg="#ECF0F1",
            font=("Courier", 9)
        )
        self.listboxFiles.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listboxFiles.yview)
        
        # Action buttons
        buttonFrame = tk.Frame(filesFrame, bg="#34495E")
        buttonFrame.pack(pady=5)
        
        buttons = [
            (self._translate('add_pdfs'), self._selectInputFiles, "#3498DB"),
            (self._translate('remove'), self._removeSelectedFiles, "#E74C3C"),
            (self._translate('move_up'), self._moveUp, "#95A5A6"),
            (self._translate('move_down'), self._moveDown, "#95A5A6"),
            (self._translate('clear_all'), self._clearAll, "#C0392B")
        ]
        
        for text, command, color in buttons:
            tk.Button(
                buttonFrame,
                text=text,
                command=command,
                bg=color,
                fg="white",
                padx=10,
                pady=5
            ).pack(side=tk.LEFT, padx=2)
        
    def _createBasicParamsSection(self, parent):
        """Create basic layout parameters section."""
        paramsFrame = tk.LabelFrame(
            parent,
            text=self._translate('layout_params'),
            bg="#34495E",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=10
        )
        paramsFrame.pack(fill=tk.X, pady=5)
        
        # Layout mode selector
        modeFrame = tk.Frame(paramsFrame, bg="#34495E")
        modeFrame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            modeFrame,
            text=self._translate('layout_mode'),
            bg="#34495E",
            fg="white",
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT, padx=5)
        
        modeMenu = ttk.Combobox(
            modeFrame,
            textvariable=self.layoutMode,
            values=['grid', 'target_pages'],
            state="readonly",
            width=25
        )
        modeMenu.pack(side=tk.LEFT, padx=5)
        modeMenu.bind("<<ComboboxSelected>>", self._toggleLayoutMode)
        
        # Create frames for both modes
        self.gridControlsFrame = tk.Frame(paramsFrame, bg="#34495E")
        self.targetPagesFrame = tk.Frame(paramsFrame, bg="#34495E")
        
        # Grid mode controls
        self._createGridControls()
        
        # Target pages mode controls
        self._createTargetPagesControls()
        
        # Show grid mode by default
        self.gridControlsFrame.pack(fill=tk.X)
        
        # Separation (common to both modes)
        self._createSeparationControl(paramsFrame)
    
    def _createGridControls(self):
        """Create grid mode controls (rows and columns)."""
        # Rows
        rowFrame = tk.Frame(self.gridControlsFrame, bg="#34495E")
        rowFrame.pack(fill=tk.X, pady=3)
        
        tk.Label(
            rowFrame,
            text=self._translate('rows'),
            bg="#34495E",
            fg="white",
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            rowFrame,
            text="−",
            command=lambda: self._adjustValue(self.rows, -1, 1, None),
            bg="#95A5A6",
            fg="white",
            width=3
        ).pack(side=tk.LEFT, padx=2)
        
        self.rowsLabel = tk.Label(
            rowFrame,
            text="1",
            bg="#ECF0F1",
            width=5,
            relief=tk.SUNKEN
        )
        self.rowsLabel.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            rowFrame,
            text="+",
            command=lambda: self._adjustValue(self.rows, 1, 1, None),
            bg="#95A5A6",
            fg="white",
            width=3
        ).pack(side=tk.LEFT, padx=2)
        
        # Columns
        colFrame = tk.Frame(self.gridControlsFrame, bg="#34495E")
        colFrame.pack(fill=tk.X, pady=3)
        
        tk.Label(
            colFrame,
            text=self._translate('columns'),
            bg="#34495E",
            fg="white",
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            colFrame,
            text="−",
            command=lambda: self._adjustValue(self.cols, -1, 1, None),
            bg="#95A5A6",
            fg="white",
            width=3
        ).pack(side=tk.LEFT, padx=2)
        
        self.colsLabel = tk.Label(
            colFrame,
            text="1",
            bg="#ECF0F1",
            width=5,
            relief=tk.SUNKEN
        )
        self.colsLabel.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            colFrame,
            text="+",
            command=lambda: self._adjustValue(self.cols, 1, 1, None),
            bg="#95A5A6",
            fg="white",
            width=3
        ).pack(side=tk.LEFT, padx=2)
    
    def _createTargetPagesControls(self):
        """Create target pages mode controls."""
        targetFrame = tk.Frame(self.targetPagesFrame, bg="#34495E")
        targetFrame.pack(fill=tk.X, pady=3)
        
        tk.Label(
            targetFrame,
            text=self._translate('target_pages'),
            bg="#34495E",
            fg="white",
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            targetFrame,
            text="−",
            command=lambda: self._adjustValue(self.targetPages, -1, 1, 1000),
            bg="#95A5A6",
            fg="white",
            width=3
        ).pack(side=tk.LEFT, padx=2)
        
        self.targetLabel = tk.Label(
            targetFrame,
            text="1",
            bg="#ECF0F1",
            width=5,
            relief=tk.SUNKEN
        )
        self.targetLabel.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            targetFrame,
            text="+",
            command=lambda: self._adjustValue(self.targetPages, 1, 1, 1000),
            bg="#95A5A6",
            fg="white",
            width=3
        ).pack(side=tk.LEFT, padx=2)
        
        # Calculated grid info
        self.calcGridLabel = tk.Label(
            self.targetPagesFrame,
            text="",
            bg="#34495E",
            fg="#3498DB",
            font=("Arial", 9, "italic")
        )
        self.calcGridLabel.pack(fill=tk.X, pady=3)
    
    def _createSeparationControl(self, parent):
        """Create separation pages control."""
        sepFrame = tk.Frame(parent, bg="#34495E")
        sepFrame.pack(fill=tk.X, pady=3)
        
        tk.Label(
            sepFrame,
            text=self._translate('separation'),
            bg="#34495E",
            fg="white",
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            sepFrame,
            text="−",
            command=lambda: self._adjustValue(self.separation, -1, 0, 20),
            bg="#95A5A6",
            fg="white",
            width=3
        ).pack(side=tk.LEFT, padx=2)
        
        self.sepLabel = tk.Label(
            sepFrame,
            text="0",
            bg="#ECF0F1",
            width=5,
            relief=tk.SUNKEN
        )
        self.sepLabel.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            sepFrame,
            text="+",
            command=lambda: self._adjustValue(self.separation, 1, 0, 20),
            bg="#95A5A6",
            fg="white",
            width=3
        ).pack(side=tk.LEFT, padx=2)
    
    def _toggleLayoutMode(self, event=None):
        """Switch between grid and target pages mode."""
        if self.layoutMode.get() == 'grid':
            self.targetPagesFrame.pack_forget()
            self.gridControlsFrame.pack(fill=tk.X, before=self.targetPagesFrame.master.winfo_children()[-1])
        else:  # target_pages
            self.gridControlsFrame.pack_forget()
            self.targetPagesFrame.pack(fill=tk.X, before=self.targetPagesFrame.master.winfo_children()[-1])
            self._updateCalculatedGrid()
    
    def _updateCalculatedGrid(self):
        """Update the calculated grid display for target pages mode."""
        inputPdfs = list(self.listboxFiles.get(0, tk.END))
        if not inputPdfs:
            self.calcGridLabel.config(text="")
            return
        
        try:
            totalPages = _countTotalPages(inputPdfs, self.separation.get())
            rows, cols = calculateOptimalGrid(totalPages, self.targetPages.get())
            self.calcGridLabel.config(text=self._translate('calculated_grid').format(rows, cols))
        except:
            self.calcGridLabel.config(text="")
    
    def _adjustValue(self, var, delta, minVal, maxVal):
        """
        Adjust numeric value with +/- buttons.
        
        Args:
            var: IntVar to modify
            delta: Amount to add/subtract
            minVal: Minimum allowed value
            maxVal: Maximum allowed value (None for no limit)
        """
        newVal = var.get() + delta
        if maxVal is None or minVal <= newVal <= maxVal:
            if newVal >= minVal:
                var.set(newVal)
                
                # Update corresponding label
                if var == self.rows:
                    self.rowsLabel.config(text=str(newVal))
                elif var == self.cols:
                    self.colsLabel.config(text=str(newVal))
                elif var == self.separation:
                    self.sepLabel.config(text=str(newVal))
                    if self.layoutMode.get() == 'target_pages':
                        self._updateCalculatedGrid()
                elif var == self.targetPages:
                    self.targetLabel.config(text=str(newVal))
                    self._updateCalculatedGrid()
            
    def _createAdvancedOptionsSection(self, parent):
        """Create advanced options section."""
        advancedFrame = tk.LabelFrame(
            parent,
            text=self._translate('advanced_options'),
            bg="#34495E",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=10
        )
        advancedFrame.pack(fill=tk.X, pady=5)
        
        # Page order
        orderFrame = tk.Frame(advancedFrame, bg="#34495E")
        orderFrame.pack(fill=tk.X, pady=3)
        
        tk.Label(
            orderFrame,
            text=self._translate('page_order'),
            bg="#34495E",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        orderMenu = ttk.Combobox(
            orderFrame,
            textvariable=self.pageOrder,
            values=[self._translate('horizontal'), self._translate('vertical')],
            state="readonly",
            width=12
        )
        orderMenu.pack(side=tk.LEFT, padx=5)
        
        # Quality preset
        qualityFrame = tk.Frame(advancedFrame, bg="#34495E")
        qualityFrame.pack(fill=tk.X, pady=3)
        
        tk.Label(
            qualityFrame,
            text=self._translate('quality_preset'),
            bg="#34495E",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        qualityMenu = ttk.Combobox(
            qualityFrame,
            textvariable=self.quality,
            values=[
                self._translate('low'),
                self._translate('medium'),
                self._translate('high'),
                self._translate('maximum')
            ],
            state="readonly",
            width=12
        )
        qualityMenu.pack(side=tk.LEFT, padx=5)
        
        # Grid options
        gridOptFrame = tk.Frame(advancedFrame, bg="#34495E")
        gridOptFrame.pack(fill=tk.X, pady=3)
        
        tk.Label(
            gridOptFrame,
            text=self._translate('grid'),
            bg="#34495E",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        gridMenu = ttk.Combobox(
            gridOptFrame,
            textvariable=self.gridOption,
            values=[self._translate('show'), self._translate('hide')],
            state="readonly",
            width=8
        )
        gridMenu.pack(side=tk.LEFT, padx=5)
        
        self.colorDisplay = tk.Label(
            gridOptFrame,
            width=3,
            bg=self.gridColor.get(),
            relief=tk.RAISED
        )
        self.colorDisplay.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            gridOptFrame,
            text=self._translate('choose_color'),
            command=self._chooseGridColor,
            bg="#9B59B6",
            fg="white",
            padx=8,
            pady=3
        ).pack(side=tk.LEFT, padx=5)
        
        # Checkboxes
        checkFrame = tk.Frame(advancedFrame, bg="#34495E")
        checkFrame.pack(fill=tk.X, pady=3)
        
        tk.Checkbutton(
            checkFrame,
            text=self._translate('maintain_aspect'),
            variable=self.maintainAspect,
            bg="#34495E",
            fg="white",
            selectcolor="#2C3E50"
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Checkbutton(
            checkFrame,
            text=self._translate('add_page_numbers'),
            variable=self.addPageNumbers,
            bg="#34495E",
            fg="white",
            selectcolor="#2C3E50"
        ).pack(side=tk.LEFT, padx=10)
        
    def _createOutputSection(self, parent):
        """Create output options section."""
        outputFrame = tk.LabelFrame(
            parent,
            text=self._translate('output_options'),
            bg="#34495E",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=10
        )
        outputFrame.pack(fill=tk.X, pady=5)
        
        # Output folder
        folderFrame = tk.Frame(outputFrame, bg="#34495E")
        folderFrame.pack(fill=tk.X, pady=3)
        
        tk.Label(
            folderFrame,
            text=self._translate('folder'),
            bg="#34495E",
            fg="white",
            width=10
        ).pack(side=tk.LEFT)
        
        self.folderEntry = tk.Entry(folderFrame, textvariable=self.outputFolder)
        self.folderEntry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.folderEntry.delete(0, tk.END)
        self.folderEntry.insert(0, self._translate('default_folder'))
        self.folderEntry.config(fg='gray')
        self.folderEntry.bind('<FocusIn>', self._clearPlaceholderFolder)
        self.folderEntry.bind('<FocusOut>', self._restorePlaceholderFolder)
        
        tk.Button(
            folderFrame,
            text=self._translate('browse'),
            command=self._selectOutputFolder,
            bg="#1ABC9C",
            fg="white",
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        # PDF name
        nameFrame = tk.Frame(outputFrame, bg="#34495E")
        nameFrame.pack(fill=tk.X, pady=3)
        
        tk.Label(
            nameFrame,
            text=self._translate('filename'),
            bg="#34495E",
            fg="white",
            width=10
        ).pack(side=tk.LEFT)
        
        self.nameEntry = tk.Entry(nameFrame, textvariable=self.pdfName)
        self.nameEntry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.nameEntry.delete(0, tk.END)
        self.nameEntry.insert(0, self._translate('default_filename'))
        self.nameEntry.config(fg='gray')
        self.nameEntry.bind('<FocusIn>', self._clearPlaceholderName)
        self.nameEntry.bind('<FocusOut>', self._restorePlaceholderName)
        
    def _createActionButtons(self, parent):
        """Create preview and create PDF action buttons."""
        actionFrame = tk.Frame(parent, bg="#2C3E50")
        actionFrame.pack(pady=15)
        
        tk.Button(
            actionFrame,
            text=self._translate('preview'),
            command=self._previewPdf,
            bg="#E67E22",
            fg="white",
            padx=20,
            pady=10,
            font=("Arial", 11, "bold")
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            actionFrame,
            text=self._translate('create_pdf'),
            command=self._createFinalOutput,
            bg="#27AE60",
            fg="white",
            padx=20,
            pady=10,
            font=("Arial", 11, "bold")
        ).pack(side=tk.LEFT, padx=10)
        
    def _createStatusBar(self):
        """Create status bar at bottom of window."""
        self.statusBar = tk.Label(
            self.root,
            text=self._translate('ready'),
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg="#34495E",
            fg="white"
        )
        self.statusBar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def _updateStatus(self, message):
        """
        Update status bar message.
        
        Args:
            message: Status message to display
        """
        self.statusBar.config(text=message)
        self.root.update_idletasks()
        
    def _selectInputFiles(self):
        """Open file dialog to select PDF files."""
        files = filedialog.askopenfilenames(
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        for file in files:
            if file not in self.listboxFiles.get(0, tk.END):
                self.listboxFiles.insert(tk.END, file)
        
        self._updateStatus(self._translate('added_files').format(len(files)))
        
        if self.layoutMode.get() == 'target_pages':
            self._updateCalculatedGrid()
        
    def _removeSelectedFiles(self):
        """Remove selected files from the list."""
        selected = self.listboxFiles.curselection()
        for index in reversed(selected):
            self.listboxFiles.delete(index)
        
        self._updateStatus(self._translate('removed_files'))
        
        if self.layoutMode.get() == 'target_pages':
            self._updateCalculatedGrid()
        
    def _moveUp(self):
        """Move selected file up in the list."""
        selected = self.listboxFiles.curselection()
        if not selected or selected[0] == 0:
            return
        
        for index in selected:
            item = self.listboxFiles.get(index)
            self.listboxFiles.delete(index)
            self.listboxFiles.insert(index - 1, item)
            self.listboxFiles.selection_set(index - 1)
            
    def _moveDown(self):
        """Move selected file down in the list."""
        selected = self.listboxFiles.curselection()
        if not selected or selected[-1] == self.listboxFiles.size() - 1:
            return
        
        for index in reversed(selected):
            item = self.listboxFiles.get(index)
            self.listboxFiles.delete(index)
            self.listboxFiles.insert(index + 1, item)
            self.listboxFiles.selection_set(index + 1)
            
    def _clearAll(self):
        """Clear all files from the list after confirmation."""
        if self.listboxFiles.size() > 0:
            if messagebox.askyesno(
                self._translate('confirm'),
                self._translate('clear_all_confirm')
            ):
                self.listboxFiles.delete(0, tk.END)
                self._updateStatus(self._translate('cleared_files'))
                
                if self.layoutMode.get() == 'target_pages':
                    self._updateCalculatedGrid()
                
    def _chooseGridColor(self):
        """Open color picker for grid color selection."""
        color = colorchooser.askcolor(color=self.gridColor.get())[1]
        if color:
            self.gridColor.set(color)
            self.colorDisplay.config(bg=color)
            
    def _applyQualityPreset(self):
        """
        Get compression percentage from quality preset.
        
        Returns:
            Integer compression percentage (25-100)
        """
        presets = {
            self._translate('low'): 50,
            self._translate('medium'): 75,
            self._translate('high'): 100,
            self._translate('maximum'): 100
        }
        return presets.get(self.quality.get(), 100)
        
    def _selectOutputFolder(self):
        """Open folder selection dialog."""
        folder = filedialog.askdirectory()
        if folder:
            self.outputFolder.set(folder)
            self.folderEntry.delete(0, tk.END)
            self.folderEntry.insert(0, folder)
            self.folderEntry.config(fg='black')
            
    def _clearPlaceholderFolder(self, event):
        """Clear folder placeholder text on focus."""
        currentText = self.folderEntry.get()
        if currentText == self._translate('default_folder'):
            self.folderEntry.delete(0, tk.END)
            self.folderEntry.config(fg='black')
            
    def _restorePlaceholderFolder(self, event):
        """Restore folder placeholder text if empty."""
        if not self.folderEntry.get():
            self.folderEntry.insert(0, self._translate('default_folder'))
            self.folderEntry.config(fg='gray')
            
    def _clearPlaceholderName(self, event):
        """Clear filename placeholder text on focus."""
        currentText = self.nameEntry.get()
        if currentText == self._translate('default_filename'):
            self.nameEntry.delete(0, tk.END)
            self.nameEntry.config(fg='black')
            
    def _restorePlaceholderName(self, event):
        """Restore filename placeholder text if empty."""
        if not self.nameEntry.get():
            self.nameEntry.insert(0, self._translate('default_filename'))
            self.nameEntry.config(fg='gray')
    
    def _getConfigFromGui(self):
        """
        Build CompactionConfig from GUI settings.
        
        Returns:
            CompactionConfig object with current GUI settings
        """
        # Parse grid color
        try:
            colorHex = self.gridColor.get()
            gridColor = tuple(int(colorHex[i:i+2], 16)/255 for i in (1, 3, 5))
        except:
            gridColor = (0, 0, 0)
        
        # Determine page order
        pageOrderValue = (
            PageOrder.HORIZONTAL 
            if self.pageOrder.get() == self._translate('horizontal')
            else PageOrder.VERTICAL
        )
        
        # Determine layout mode
        layoutModeValue = (
            LayoutMode.GRID
            if self.layoutMode.get() == 'grid'
            else LayoutMode.TARGET_PAGES
        )
        
        # Get output folder
        outputDir = self.outputFolder.get()
        if not outputDir or outputDir in [
            self._translate('default_folder'),
            TRANSLATIONS['en']['default_folder'],
            TRANSLATIONS['fr']['default_folder']
        ]:
            outputDir = None
        
        # Get filename
        filename = self.pdfName.get()
        if not filename or filename in [
            self._translate('default_filename'),
            TRANSLATIONS['en']['default_filename'],
            TRANSLATIONS['fr']['default_filename']
        ]:
            filename = None
        
        return CompactionConfig(
            rows=self.rows.get(),
            columns=self.cols.get(),
            targetPages=self.targetPages.get(),
            layoutMode=layoutModeValue,
            compression=self._applyQualityPreset(),
            separationPages=self.separation.get(),
            pageOrder=pageOrderValue,
            maintainAspectRatio=self.maintainAspect.get(),
            showGrid=(self.gridOption.get() == self._translate('show')),
            gridColor=gridColor,
            addPageNumbers=self.addPageNumbers.get(),
            outputDir=outputDir,
            outputFilename=filename
        )
    
    def _previewPdf(self):
        """Generate and display preview of first output page."""
        inputPdfs = list(self.listboxFiles.get(0, tk.END))
        if not inputPdfs:
            messagebox.showerror(
                self._translate('error'),
                self._translate('no_files_error')
            )
            return
            
        try:
            self._updateStatus(self._translate('preview_generating'))
            
            config = self._getConfigFromGui()
            rows, columns = _getLayoutParameters(config, inputPdfs)
            
            cellWidth = A4_WIDTH / columns
            cellHeight = A4_HEIGHT / rows
            
            # Open documents
            docs = [fitz.open(pdf) for pdf in inputPdfs]
            
            # Merge pages
            allPages = mergePdfPages(docs, config.compression, config.separationPages)
            previewPages = allPages[:columns * rows]
            
            # Create preview document
            newDoc = fitz.open()
            newPage = newDoc.new_page(width=A4_WIDTH, height=A4_HEIGHT)
            
            # Place pages
            for idx, pixmap in enumerate(previewPages):
                if pixmap is not None:
                    _placePageOnGrid(
                        newPage,
                        pixmap,
                        idx,
                        columns,
                        rows,
                        cellWidth,
                        cellHeight,
                        config.pageOrder,
                        config.maintainAspectRatio,
                        config.addPageNumbers
                    )
            
            # Draw grid if enabled
            if config.showGrid:
                _drawGrid(newPage, columns, rows, cellWidth, cellHeight, config.gridColor)
            
            # Close input documents
            for doc in docs:
                doc.close()
            
            # Save to temp file and render
            tempDir = tempfile.gettempdir()
            tempPdf = os.path.join(tempDir, "preview_temp.pdf")
            newDoc.save(tempPdf)
            
            pixPreview = newDoc[0].get_pixmap()
            newDoc.close()
            
            # Create PIL image
            img = Image.frombytes(
                "RGB",
                [pixPreview.width, pixPreview.height],
                pixPreview.samples
            )
            img.thumbnail((800, 600), Image.Resampling.LANCZOS)
            
            # Show preview window
            previewWin = Toplevel(self.root)
            previewWin.title(self._translate('preview_title'))
            previewWin.configure(bg="#2C3E50")
            
            canvas = Canvas(
                previewWin,
                width=img.width,
                height=img.height,
                bg="#2C3E50"
            )
            canvas.pack(padx=10, pady=10)
            
            imgTk = ImageTk.PhotoImage(img)
            canvas.create_image(0, 0, anchor=tk.NW, image=imgTk)
            canvas.image = imgTk
            
            # Clean up temp file
            try:
                os.remove(tempPdf)
            except:
                pass
                
            self._updateStatus(self._translate('preview_success'))
            
        except Exception as e:
            messagebox.showerror(
                self._translate('error'),
                f"{self._translate('preview_failed')}:\n{str(e)}"
            )
            self._updateStatus(self._translate('preview_failed'))
    
    def _createFinalOutput(self):
        """Create final PDF output using core library."""
        inputPdfs = list(self.listboxFiles.get(0, tk.END))
        if not inputPdfs:
            messagebox.showerror(
                self._translate('error'),
                self._translate('no_files_error')
            )
            return
            
        try:
            self._updateStatus(self._translate('creating_pdf'))
            
            config = self._getConfigFromGui()
            outputPath = compactPdfs(inputPdfs, config)
            
            self._updateStatus(
                self._translate('pdf_saved').format(os.path.basename(outputPath))
            )
            
            messagebox.showinfo(
                self._translate('success'),
                f"{self._translate('pdf_created')}\n\n"
                f"{self._translate('saved_to')}\n{outputPath}"
            )
            
        except Exception as e:
            messagebox.showerror(
                self._translate('error'),
                f"{self._translate('pdf_failed')}:\n{str(e)}"
            )
            self._updateStatus(self._translate('pdf_failed'))


def launchGui():
    """
    Launch the PDF Compactor GUI application.
    
    This is the main entry point for the GUI. Call this function to start
    the interactive PDF compaction interface.
    
    Example:
        >>> from vicutils.pdf import launchGui
        >>> launchGui()
    """
    root = tk.Tk()
    app = PdfCompactorApp(root)
    root.mainloop()
    