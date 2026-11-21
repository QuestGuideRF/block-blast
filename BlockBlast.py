import sys
import json
import random
import math
from typing import List ,Tuple ,Optional ,Set
from dataclasses import dataclass
from pathlib import Path
from PyQt6 .QtWidgets import (
QApplication ,QMainWindow ,QWidget ,QVBoxLayout ,QHBoxLayout ,
QLabel ,QPushButton ,QFrame ,QGridLayout ,QMessageBox
)
from PyQt6 .QtCore import (
Qt ,QTimer ,QPropertyAnimation ,QEasingCurve ,pyqtSignal ,
QRect ,QPoint ,QSize ,QSequentialAnimationGroup ,QParallelAnimationGroup ,
QMimeData
)
from PyQt6 .QtGui import (
QPainter ,QColor ,QPen ,QBrush ,QFont ,QPalette ,QLinearGradient ,
QMouseEvent ,QPaintEvent ,QDragEnterEvent ,QDropEvent ,QDragMoveEvent ,
QDrag ,QPixmap
)
@dataclass
class Position :
    row :int
    col :int
    def __add__ (self ,other ):
        return Position (self .row +other .row ,self .col +other .col )
class GameFigure :
    FIGURES ={
    'single':[(0 ,0 )],
    'line2_h':[(0 ,0 ),(0 ,1 )],
    'line2_v':[(0 ,0 ),(1 ,0 )],
    'line3_h':[(0 ,0 ),(0 ,1 ),(0 ,2 )],
    'line3_v':[(0 ,0 ),(1 ,0 ),(2 ,0 )],
    'line4_h':[(0 ,0 ),(0 ,1 ),(0 ,2 ),(0 ,3 )],
    'line4_v':[(0 ,0 ),(1 ,0 ),(2 ,0 ),(3 ,0 )],
    'line5_h':[(0 ,0 ),(0 ,1 ),(0 ,2 ),(0 ,3 ),(0 ,4 )],
    'line5_v':[(0 ,0 ),(1 ,0 ),(2 ,0 ),(3 ,0 ),(4 ,0 )],
    'square2x2':[(0 ,0 ),(0 ,1 ),(1 ,0 ),(1 ,1 )],
    'square3x3':[(0 ,0 ),(0 ,1 ),(0 ,2 ),(1 ,0 ),(1 ,1 ),(1 ,2 ),(2 ,0 ),(2 ,1 ),(2 ,2 )],
    'L_shape':[(0 ,0 ),(1 ,0 ),(2 ,0 ),(2 ,1 )],
    'L_mirror':[(0 ,0 ),(1 ,0 ),(2 ,0 ),(2 ,-1 )],
    'L_rotated':[(0 ,0 ),(0 ,1 ),(0 ,2 ),(1 ,0 )],
    'L_rotated_mirror':[(0 ,0 ),(0 ,1 ),(0 ,2 ),(-1 ,0 )],
    'T_shape':[(0 ,0 ),(0 ,1 ),(0 ,2 ),(1 ,1 )],
    'T_upside':[(0 ,1 ),(1 ,0 ),(1 ,1 ),(1 ,2 )],
    'T_left':[(0 ,0 ),(1 ,0 ),(2 ,0 ),(1 ,-1 )],
    'T_right':[(0 ,0 ),(1 ,0 ),(2 ,0 ),(1 ,1 )],
    'corner_small':[(0 ,0 ),(0 ,1 ),(1 ,0 )],
    'corner_big':[(0 ,0 ),(0 ,1 ),(0 ,2 ),(1 ,0 ),(2 ,0 )],
    'Z_shape':[(0 ,0 ),(0 ,1 ),(1 ,1 ),(1 ,2 )],
    'Z_mirror':[(0 ,1 ),(0 ,2 ),(1 ,0 ),(1 ,1 )],
    }
    COLORS =[
    QColor (255 ,87 ,87 ),
    QColor (87 ,165 ,255 ),
    QColor (87 ,255 ,87 ),
    QColor (255 ,206 ,87 ),
    QColor (255 ,87 ,255 ),
    QColor (87 ,255 ,255 ),
    QColor (255 ,165 ,87 ),
    QColor (165 ,87 ,255 ),
    ]
    def __init__ (self ,shape_name :str =None ):
        if shape_name is None :
            shape_name =random .choice (list (self .FIGURES .keys ()))
        self .shape_name =shape_name
        self .blocks =[Position (r ,c )for r ,c in self .FIGURES [shape_name ]]
        self .color =random .choice (self .COLORS )
        self .is_placed =False
    def get_bounding_box (self )->Tuple [int ,int ,int ,int ]:
        min_r =min (block .row for block in self .blocks )
        max_r =max (block .row for block in self .blocks )
        min_c =min (block .col for block in self .blocks )
        max_c =max (block .col for block in self .blocks )
        return min_r ,max_r ,min_c ,max_c
    def get_size (self )->Tuple [int ,int ]:
        min_r ,max_r ,min_c ,max_c =self .get_bounding_box ()
        return max_r -min_r +1 ,max_c -min_c +1
class GameCell (QWidget ):
    clicked =pyqtSignal (int ,int )
    def __init__ (self ,row :int ,col :int ,parent =None ):
        super ().__init__ (parent )
        self .row =row
        self .col =col
        self .is_filled =False
        self .color =QColor (40 ,40 ,40 )
        self .highlight =False
        self .setFixedSize (35 ,35 )
        self .setAcceptDrops (True )
    def set_filled (self ,filled :bool ,color :QColor =None ):
        self .is_filled =filled
        if color and filled :
            self .color =color
        else :
            self .color =QColor (40 ,40 ,40 )
        self .update ()
    def set_highlight (self ,highlight :bool ):
        self .highlight =highlight
        self .update ()
    def paintEvent (self ,event :QPaintEvent ):
        painter =QPainter (self )
        painter .setRenderHint (QPainter .RenderHint .Antialiasing )
        if self .is_filled :
            gradient =QLinearGradient (0 ,0 ,self .width (),self .height ())
            lighter =self .color .lighter (120 )
            darker =self .color .darker (120 )
            gradient .setColorAt (0 ,lighter )
            gradient .setColorAt (1 ,darker )
            painter .setBrush (QBrush (gradient ))
            painter .setPen (QPen (self .color .darker (150 ),2 ))
        else :
            painter .setBrush (QBrush (QColor (25 ,25 ,25 )))
            painter .setPen (QPen (QColor (60 ,60 ,60 ),1 ))
        if self .highlight :
            painter .setBrush (QBrush (QColor (100 ,200 ,100 ,100 )))
            painter .setPen (QPen (QColor (100 ,255 ,100 ),2 ))
        painter .drawRoundedRect (2 ,2 ,self .width ()-4 ,self .height ()-4 ,4 ,4 )
        if self .is_filled :
            painter .setBrush (QBrush (QColor (255 ,255 ,255 ,30 )))
            painter .setPen (Qt .PenStyle .NoPen )
            painter .drawRoundedRect (4 ,4 ,self .width ()-16 ,self .height ()//3 ,2 ,2 )
class FigurePreview (QWidget ):
    figure_selected =pyqtSignal (object )
    def __init__ (self ,figure :GameFigure ,parent =None ):
        super ().__init__ (parent )
        self .figure =figure
        self .is_available =True
        self .setFixedSize (120 ,120 )
        self .setAcceptDrops (False )
        self .drag_start_position =None
    def set_available (self ,available :bool ):
        self .is_available =available
        self .update ()
    def paintEvent (self ,event :QPaintEvent ):
        if not self .figure or self .figure .is_placed :
            return
        painter =QPainter (self )
        painter .setRenderHint (QPainter .RenderHint .Antialiasing )
        bg_color =QColor (45 ,45 ,45 )if self .is_available else QColor (30 ,30 ,30 )
        painter .fillRect (self .rect (),bg_color )
        block_size =20
        min_r ,max_r ,min_c ,max_c =self .figure .get_bounding_box ()
        figure_width =(max_c -min_c +1 )*block_size
        figure_height =(max_r -min_r +1 )*block_size
        start_x =(self .width ()-figure_width )//2 -min_c *block_size
        start_y =(self .height ()-figure_height )//2 -min_r *block_size
        color =self .figure .color if self .is_available else self .figure .color .darker (200 )
        for block in self .figure .blocks :
            x =start_x +block .col *block_size
            y =start_y +block .row *block_size
            gradient =QLinearGradient (x ,y ,x +block_size ,y +block_size )
            gradient .setColorAt (0 ,color .lighter (120 ))
            gradient .setColorAt (1 ,color .darker (120 ))
            painter .setBrush (QBrush (gradient ))
            painter .setPen (QPen (color .darker (150 ),1 ))
            painter .drawRoundedRect (x +1 ,y +1 ,block_size -2 ,block_size -2 ,3 ,3 )
            if self .is_available :
                painter .setBrush (QBrush (QColor (255 ,255 ,255 ,40 )))
                painter .setPen (Qt .PenStyle .NoPen )
                painter .drawRoundedRect (x +3 ,y +3 ,block_size -10 ,block_size //3 ,2 ,2 )
    def mousePressEvent (self ,event :QMouseEvent ):
        if event .button ()==Qt .MouseButton .LeftButton and self .is_available and not self .figure .is_placed :
            self .drag_start_position =event .position ().toPoint ()
            self .figure_selected .emit (self .figure )
    def mouseMoveEvent (self ,event :QMouseEvent ):
        if not (event .buttons ()&Qt .MouseButton .LeftButton ):
            return
        if not self .drag_start_position :
            return
        if not self .is_available or not self .figure or self .figure .is_placed :
            return
        if ((event .position ().toPoint ()-self .drag_start_position ).manhattanLength ()<
        QApplication .startDragDistance ()):
            return
        drag =QDrag (self )
        mime_data =QMimeData ()
        mime_data .setText (f"figure_{id (self .figure )}")
        drag .setMimeData (mime_data )
        pixmap =QPixmap (120 ,120 )
        pixmap .fill (Qt .GlobalColor .transparent )
        painter =QPainter (pixmap )
        painter .setRenderHint (QPainter .RenderHint .Antialiasing )
        block_size =20
        min_r ,max_r ,min_c ,max_c =self .figure .get_bounding_box ()
        figure_width =(max_c -min_c +1 )*block_size
        figure_height =(max_r -min_r +1 )*block_size
        start_x =(120 -figure_width )//2 -min_c *block_size
        start_y =(120 -figure_height )//2 -min_r *block_size
        for block in self .figure .blocks :
            x =start_x +block .col *block_size
            y =start_y +block .row *block_size
            painter .setBrush (QBrush (self .figure .color ))
            painter .setPen (QPen (self .figure .color .darker (150 ),1 ))
            painter .drawRoundedRect (x +1 ,y +1 ,block_size -2 ,block_size -2 ,3 ,3 )
        painter .end ()
        drag .setPixmap (pixmap )
        drag .setHotSpot (self .drag_start_position )
        result =drag .exec (Qt .DropAction .MoveAction )
        if result ==Qt .DropAction .MoveAction :
            pass
class GameBoard (QWidget ):
    figure_placed =pyqtSignal ()
    game_over =pyqtSignal ()
    lines_cleared =pyqtSignal (int )
    def __init__ (self ,parent =None ):
        super ().__init__ (parent )
        self .grid_size =9
        self .cells =[]
        self .current_figure =None
        self .preview_positions =[]
        self .game_window =None
        self .init_ui ()
        self .init_grid ()
    def init_ui (self ):
        self .setFixedSize (9 *35 +20 ,9 *35 +20 )
        self .setAcceptDrops (True )
        self .setStyleSheet ("цвет фона: RGB(20, 20, 20);")
    def init_grid (self ):
        layout =QGridLayout ()
        layout .setSpacing (2 )
        layout .setContentsMargins (10 ,10 ,10 ,10 )
        for row in range (self .grid_size ):
            cell_row =[]
            for col in range (self .grid_size ):
                cell =GameCell (row ,col ,self )
                cell .clicked .connect (self .cell_clicked )
                layout .addWidget (cell ,row ,col )
                cell_row .append (cell )
            self .cells .append (cell_row )
        self .setLayout (layout )
    def cell_clicked (self ,row :int ,col :int ):
        if self .current_figure :
            self .try_place_figure (row ,col )
    def try_place_figure (self ,row :int ,col :int )->bool :
        if not self .current_figure or self .current_figure .is_placed :
            return False
        for block in self .current_figure .blocks :
            new_row =row +block .row
            new_col =col +block .col
            if (new_row <0 or new_row >=self .grid_size or
            new_col <0 or new_col >=self .grid_size or
            self .cells [new_row ][new_col ].is_filled ):
                return False
        for block in self .current_figure .blocks :
            new_row =row +block .row
            new_col =col +block .col
            self .cells [new_row ][new_col ].set_filled (True ,self .current_figure .color )
        self .current_figure .is_placed =True
        self .current_figure =None
        self .clear_preview ()
        cleared_lines =self .check_and_clear_lines ()
        if cleared_lines >0 :
            self .lines_cleared .emit (cleared_lines )
        self .figure_placed .emit ()
        return True
    def can_place_figure (self ,figure :GameFigure ,row :int ,col :int )->bool :
        if not figure or figure .is_placed :
            return False
        for block in figure .blocks :
            new_row =row +block .row
            new_col =col +block .col
            if (new_row <0 or new_row >=self .grid_size or
            new_col <0 or new_col >=self .grid_size or
            self .cells [new_row ][new_col ].is_filled ):
                return False
        return True
    def can_place_any_figure (self ,figures :List [GameFigure ])->bool :
        for figure in figures :
            if figure .is_placed :
                continue
            for row in range (self .grid_size ):
                for col in range (self .grid_size ):
                    if self .can_place_figure (figure ,row ,col ):
                        return True
        return False
    def set_current_figure (self ,figure :GameFigure ):
        self .current_figure =figure
        self .clear_preview ()
    def leaveEvent (self ,event ):
        self .clear_preview ()
    def show_preview (self ,row :int ,col :int ):
        self .clear_preview ()
        if not self .current_figure or self .current_figure .is_placed :
            return
        if self .can_place_figure (self .current_figure ,row ,col ):
            for block in self .current_figure .blocks :
                new_row =row +block .row
                new_col =col +block .col
                if 0 <=new_row <self .grid_size and 0 <=new_col <self .grid_size :
                    self .cells [new_row ][new_col ].set_highlight (True )
                    self .preview_positions .append ((new_row ,new_col ))
    def clear_preview (self ):
        for row ,col in self .preview_positions :
            self .cells [row ][col ].set_highlight (False )
        self .preview_positions .clear ()
    def check_and_clear_lines (self )->int :
        lines_to_clear =set ()
        for row in range (self .grid_size ):
            if all (self .cells [row ][col ].is_filled for col in range (self .grid_size )):
                lines_to_clear .add (('row',row ))
        for col in range (self .grid_size ):
            if all (self .cells [row ][col ].is_filled for row in range (self .grid_size )):
                lines_to_clear .add (('col',col ))
        if lines_to_clear :
            self .animate_line_clearing (lines_to_clear )
        return len (lines_to_clear )
    def animate_line_clearing (self ,lines_to_clear :Set [Tuple [str ,int ]]):
        cells_to_clear =[]
        for line_type ,index in lines_to_clear :
            if line_type =='row':
                for col in range (self .grid_size ):
                    cells_to_clear .append (self .cells [index ][col ])
            else :
                for row in range (self .grid_size ):
                    cells_to_clear .append (self .cells [row ][index ])
        def blink ():
            for cell in cells_to_clear :
                cell .set_filled (False )
        QTimer .singleShot (200 ,blink )
    def clear_board (self ):
        for row in range (self .grid_size ):
            for col in range (self .grid_size ):
                self .cells [row ][col ].set_filled (False )
        self .clear_preview ()
        self .current_figure =None
    def mouseMoveEvent (self ,event :QMouseEvent ):
        if self .current_figure and not self .current_figure .is_placed :
            pos =event .position ().toPoint ()
            for row in range (self .grid_size ):
                for col in range (self .grid_size ):
                    cell_rect =self .cells [row ][col ].geometry ()
                    if cell_rect .contains (pos ):
                        self .show_preview (row ,col )
                        return
            self .clear_preview ()
    def dragEnterEvent (self ,event :QDragEnterEvent ):
        if event .mimeData ().hasText ()and event .mimeData ().text ().startswith ("figure_"):
            event .acceptProposedAction ()
        else :
            event .ignore ()
    def dragMoveEvent (self ,event :QDragMoveEvent ):
        if event .mimeData ().hasText ()and event .mimeData ().text ().startswith ("figure_"):
            pos =event .position ().toPoint ()
            for row in range (self .grid_size ):
                for col in range (self .grid_size ):
                    cell_rect =self .cells [row ][col ].geometry ()
                    if cell_rect .contains (pos ):
                        self .show_preview (row ,col )
                        if self .can_place_figure (self .current_figure ,row ,col ):
                            event .acceptProposedAction ()
                        else :
                            event .ignore ()
                        return
            self .clear_preview ()
            event .ignore ()
        else :
            event .ignore ()
    def dropEvent (self ,event :QDropEvent ):
        if event .mimeData ().hasText ()and event .mimeData ().text ().startswith ("figure_"):
            pos =event .position ().toPoint ()
            for row in range (self .grid_size ):
                for col in range (self .grid_size ):
                    cell_rect =self .cells [row ][col ].geometry ()
                    if cell_rect .contains (pos ):
                        if self .try_place_figure (row ,col ):
                            event .acceptProposedAction ()
                        else :
                            event .ignore ()
                        return
            self .clear_preview ()
            event .ignore ()
        else :
            event .ignore ()
    def dragLeaveEvent (self ,event ):
        self .clear_preview ()
class ScoreDisplay (QLabel ):
    def __init__ (self ,parent =None ):
        super ().__init__ (parent )
        self .score =0
        self .high_score =self .load_high_score ()
        self .update_display ()
        self .setStyleSheet ("""            QLabel {
                            цвет: белый;
                            размер шрифта: 18 пикселей;
                            начертание шрифта: жирный;
                            отступ: 10 пикселей;
                            цвет фона: rgba(0, 0, 0, 0,3);
                            радиус границы: 10 пикселей;
                        }""")
    def add_score (self ,points :int ):
        self .score +=points
        if self .score >self .high_score :
            self .high_score =self .score
            self .save_high_score ()
        self .update_display ()
        self .setStyleSheet (self .styleSheet ()+"""
            QLabel { background-color: rgba(100, 200, 100, 0.5); }
        """)
        QTimer .singleShot (300 ,self .reset_style )
    def reset_style (self ):
        self .setStyleSheet ("""            QLabel {
                            цвет: белый;
                            размер шрифта: 18 пикселей;
                            начертание шрифта: жирный;
                            отступ: 10 пикселей;
                            цвет фона: rgba(0, 0, 0, 0,3);
                            радиус границы: 10 пикселей;
                        }""")
    def reset_score (self ):
        self .score =0
        self .update_display ()
    def update_display (self ):
        self .setText (f"Счет: {self .score }\nРекорд: {self .high_score }")
    def load_high_score (self )->int :
        try :
            with open ('block_blast_score.json','r')as f :
                data =json .load (f )
                return data .get ('high_score',0 )
        except FileNotFoundError :
            return 0
    def save_high_score (self ):
        try :
            with open ('block_blast_score.json','w')as f :
                json .dump ({'high_score':self .high_score },f )
        except Exception :
            pass
class BlockBlastGame (QMainWindow ):
    def __init__ (self ):
        super ().__init__ ()
        self .current_figures =[]
        self .figure_previews =[]
        self .init_ui ()
        self .start_new_game ()
    def init_ui (self ):
        self .setWindowTitle ("Block Blast - Точная копия")
        self .setFixedSize (800 ,700 )
        self .setStyleSheet ("""            QMainWindow {
                            фон: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                стоп:0 #1a1a2e, стоп:1 #16213e);
                        }
                        QPushButton {
                            цвет фона: #4CAF50;
                            цвет: белый;
                            граница: нет;
                            отступ: 10 пикселей 20 пикселей;
                            радиус границы: 8 пикселей;
                            размер шрифта: 14 пикселей;
                            начертание шрифта: жирный;
                        }
                        QPushButton: наведите {
                            цвет фона: #45a049;
                        }
                        QPushButton: нажал {
                            цвет фона: #3d8b40;
                        }""")
        central_widget =QWidget ()
        self .setCentralWidget (central_widget )
        main_layout =QVBoxLayout ()
        main_layout .setSpacing (20 )
        main_layout .setContentsMargins (20 ,20 ,20 ,20 )
        top_layout =QHBoxLayout ()
        self .score_display =ScoreDisplay ()
        top_layout .addWidget (self .score_display )
        top_layout .addStretch ()
        self .restart_button =QPushButton ("🔄 Новая игра")
        self .restart_button .clicked .connect (self .start_new_game )
        top_layout .addWidget (self .restart_button )
        main_layout .addLayout (top_layout )
        board_container =QHBoxLayout ()
        board_container .addStretch ()
        self .game_board =GameBoard ()
        self .game_board .game_window =self
        self .game_board .figure_placed .connect (self .on_figure_placed )
        self .game_board .lines_cleared .connect (self .on_lines_cleared )
        self .game_board .game_over .connect (self .on_game_over )
        board_container .addWidget (self .game_board )
        board_container .addStretch ()
        main_layout .addLayout (board_container )
        figures_layout =QHBoxLayout ()
        figures_layout .setSpacing (20 )
        figures_layout .addStretch ()
        for i in range (3 ):
            preview =FigurePreview (None )
            preview .figure_selected .connect (self .on_figure_selected )
            figures_layout .addWidget (preview )
            self .figure_previews .append (preview )
        figures_layout .addStretch ()
        main_layout .addLayout (figures_layout )
        central_widget .setLayout (main_layout )
    def start_new_game (self ):
        self .game_board .clear_board ()
        self .score_display .reset_score ()
        self .generate_new_figures ()
    def generate_new_figures (self ):
        self .current_figures =[]
        for i in range (3 ):
            figure =GameFigure ()
            self .current_figures .append (figure )
            self .figure_previews [i ].figure =figure
            self .figure_previews [i ].set_available (True )
            self .figure_previews [i ].update ()
        if not self .game_board .can_place_any_figure (self .current_figures ):
            self .on_game_over ()
    def on_figure_selected (self ,figure :GameFigure ):
        if figure and not figure .is_placed :
            self .game_board .set_current_figure (figure )
    def on_figure_placed (self ):
        for i ,figure in enumerate (self .current_figures ):
            if figure .is_placed :
                self .figure_previews [i ].set_available (False )
                self .figure_previews [i ].update ()
        if all (figure .is_placed for figure in self .current_figures ):
            QTimer .singleShot (500 ,self .generate_new_figures )
        available_figures =[f for f in self .current_figures if not f .is_placed ]
        if available_figures and not self .game_board .can_place_any_figure (available_figures ):
            self .on_game_over ()
    def on_lines_cleared (self ,count :int ):
        points =count *100
        if count >1 :
            points +=count *50
        self .score_display .add_score (points )
    def on_game_over (self ):
        QTimer .singleShot (1000 ,lambda :QMessageBox .information (
        self ,
        "Игра окончена!",
        f"Ваш счет: {self .score_display .score }\n"
        f"Рекорд: {self .score_display .high_score }\n\n"
        f"Нажмите 'Новая игра' для перезапуска."
        ))
def main ():
    app =QApplication (sys .argv )
    app .setApplicationName ("Блок взрыва")
    app .setStyle ('Fusion')
    palette =QPalette ()
    palette .setColor (QPalette .ColorRole .Window ,QColor (53 ,53 ,53 ))
    palette .setColor (QPalette .ColorRole .WindowText ,QColor (255 ,255 ,255 ))
    app .setPalette (palette )
    game =BlockBlastGame ()
    game .show ()
    sys .exit (app .exec ())
if __name__ =="__main__":
    main ()