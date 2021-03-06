

from PIL import Image, ImageDraw, ImageFont, _imaging
import random, sys, os


class BingoCard( object ):


  @classmethod
  def draw_several_cards( self, card, how_many=6, save_to=None, cols_per_image=3, background='white' ):

    if card.image is None:
      card.initialize_image()

    image = card.image

    rows = ( ( how_many - 1 ) // cols_per_image ) + 1

    if how_many >= cols_per_image:
      cols = cols_per_image
    else:
      cols = how_many

    iw, ih, w, h = card.width, card.height, card.width * cols, card.height * rows
    nimage = Image.new( 'RGB', ( w, h ), background )

    for row in range( rows ):
      for col in range( cols ):
        embed_image = card.print_card( save_to=None )
        nimage.paste( embed_image, ( col * iw, row * ih ) )


    if save_to is None:
      return nimage
    else:
      return nimage.save( save_to )


  def _initialize_args( self ):

    return [
        'width',
        'height',
        'header',
        'margin_top',
        'margin_left',
        'margin_right',
        'margin_bottom',
        'margin',
        'with_ref_image',
        'background',
        'draw_lines',
        'set_gap',
        'set_length'
      ]

  def _prepare_args_from_dictionary( self, _kwargs ):
    new_kwargs = { }
    for i in self._initialize_args():
      if _kwargs.has_key( i ):
        new_kwargs[ i ] = _kwargs[ i ]

    return new_kwargs


  def __init__( self, width=800, height=600, header=10, margin_top=10, margin_left=10, margin_right=10, margin_bottom=10, margin=None, with_ref_image=None, background='white', draw_lines=True, set_gap=0, set_length=1):
    self.width  = width
    self.height = height
    self.header = header
    self.with_ref_image = with_ref_image
    self.background = background
    self.font = 'Overlock-Black.ttf'
    self.draw_lines = draw_lines
    self.line_size  = 2
    self.line_color = 0
    self.text_size = None
    self.text_color = 0
    self.image  = None
    self.set_length = set_length
    self.set_gap = set_gap


    if margin is None and ( margin_left > 0 and margin_right > 0 and margin_bottom > 0 and margin_top > 0 ):
      self.margin_left    = margin_left
      self.margin_right   = margin_right
      self.margin_bottom  = margin_bottom
      self.margin_top     = margin_top
    else:
      margin = margin or 10
      self.margin_top = self.margin_left = self.margin_right = self.margin_bottom = margin


  def card_layout( self ):
    return [ ]

  def get_text_size( self ):
    if self.text_size is None:
      text_size = int( self.width / 38.4 )
    else:
      text_size	= self.text_size

    return text_size


  def get_font( self ):
    return ImageFont.truetype( self.font, self.get_text_size() )


  def get_top( self ):
    if self.header:
      top = ( self.header ) + self.margin_top
    else:
      top = self.margin_top

    return top

  # FIXME: Doesn't deal with sets yet
  def draw_lines_on_image( self, draw, layout, col_height, col_width ):
    if self.draw_lines:
      # Rows
      for i in range( len( layout ) + 1 ):
        y = ( self.get_top() + ( i * col_height ) )
        draw.line( ( self.margin_left, y, self.width - self.margin_right, y ), fill=self.line_color, width=self.line_size  )

      # Cols
      for j in range( len( layout[ 0 ] ) + 1 ):
        x = self.margin_left + ( j * col_width )
        draw.line( ( x, self.get_top(), x, self.height - self.margin_bottom ), fill=self.line_color, width=self.line_color )



  def draw( self, layout, save_to ):
    print "About to draw"

    image, width, height = self.image, self.width, self.height
    font, text_size, top = self.get_font(), self.get_text_size(), self.get_top()
    ml, mr, mt, mb = self.margin_left, self.margin_right, self.margin_top, self.margin_bottom
    sl, sg  = self.set_length, self.set_gap


    draw        = ImageDraw.Draw( image )
    col_height  = ( height - top - mb - ( ( ( len( layout ) // sl ) - 1 ) * sg ) ) / len( layout )
    col_width   = ( width - ( ml + mr ) ) / len( layout[ 0 ] )

    self.draw_lines_on_image( draw, layout, col_height, col_width )

    # Start drawing numbers
    for i in range( len( layout ) ):
      for j in range( len( layout[0] ) ):
        number = layout[ i ][ j ]

        x = ml + ( j * col_width ) + ( col_width / 2 ) - ( text_size / 2 )
        y = top + ( ( i // sl ) * sg ) + ( i * col_height ) + ( col_height / 2 ) - ( text_size / 2 )

        if number is not None:
          draw.text( ( x, y ), str( number ), fill=0, font=font )

    print "OK"

    # Save stuff
    if save_to is None:
      return image
    else:
      image.save( save_to )



  def bingo_card( self ):
    """ Needs to be implemented by the subclass """


  def initialize_image( self ):
    if( self.with_ref_image ):
      self.image = im = Image.open( self.with_ref_image )
      self.width, self.height = im.size
    else:
      self.image  = Image.new( 'RGB', ( self.width, self.height ), self.background )


  def print_card( self, save_to='test.png' ):
    self.initialize_image()
    return self.draw( self.bingo_card(), save_to )


class USBingoCard( BingoCard ):

  def __init__( self, **kwargs ):
    BingoCard.__init__( self, **self._prepare_args_from_dictionary( kwargs ) )


  def card_layout( self ):
    return [ range( i, i + 15 ) for i in range( 1, 75, 15 ) ]


  def bingo_card( self ):
    layout   = self.card_layout()
    num_of_rows = 5
    cols        = 5
    blanks      = [ ]
    possible_numbers = range( 1, 76 )

    for i in range( num_of_rows ):
      row = [ ]
      for j in range( cols ):
        flag = True
        while flag:
          number = layout[ j ][ random.randint( 0, len( layout[ j ] ) - 1 ) ]
          if number in possible_numbers:
            possible_numbers.remove( number )
            row.append( number )
            flag = False

      blanks.append( row )

    blanks[ 2 ][ 2 ] = None

    return blanks



class UKBingoCard( BingoCard ):

  def __init__( self, **kwargs ):
    BingoCard.__init__( self, **self._prepare_args_from_dictionary( kwargs ) )

    if kwargs.has_key( 'set_size' ):
      self.set_size = kwargs[ 'set_size' ]
    else:
      self.set_size = 1



  def card_layout( self ):
    return [
      range( 1, 9 + 1 ),
      range( 10, 19 + 1 ),
      range( 20, 29 + 1),
      range( 30, 39 + 1 ),
      range( 40, 49 + 1),
      range( 50, 59 + 1),
      range( 60, 69 + 1),
      range( 70, 79 + 1),
      range( 80, 90 + 1)
    ]


  def bingo_card( self ):
    layout                = self.card_layout()
    num_of_rows           = 3
    cols                  = len( self.card_layout() )
    blanks                = [ ]
    stack                 = range( 1, 91 )
    seen                  = { }

    for s in range( self.set_size ):
      for i in range( num_of_rows ):
        row = [ None ] * 9
        published_cols = {}
        for j in range( 5 ):
          val = None
          tries = 0
          while val is None:
            if tries > 20:
              break
            tries += 1
            val = random.choice( stack )
            for k in range( len( layout ) ):
              if val in layout[ k ]:
                if (published_cols.has_key( k ) and published_cols[ k ] < 4):
                  val = None
            if not seen.has_key( val ):
              for k in range( len( layout ) ):
                if val in layout[ k ]:
                  if not published_cols.has_key( k ) or (published_cols.has_key( k ) and published_cols[ k ] < 4):
                    row[ k ] = val
                    if not published_cols.has_key( k ):
                      published_cols[ k ] = 1
                    else:
                      published_cols[ k ] += 1
                    seen[ val ] = True
                    stack.remove( val )
                    break
                  else:
                    pass
            else:
              val = None

        blanks.append( row )

    if len(stack) > 0 and self.set_size == 6:
      return self.bingo_card()
    else:
      return blanks





if __name__ == '__main__':

  # A single US Card - Indigo
  o = USBingoCard( header=90, margin_top=35, margin_left=60, margin_right=65, margin_bottom=100, with_ref_image='templates/75/indigo.jpg', draw_lines=False )
  o.print_card( 'test.png' )

  # A single US Card - Blue
  o = USBingoCard( header=90, margin_top=35, margin_left=60, margin_right=65, margin_bottom=100, with_ref_image='templates/75/blue.jpg', draw_lines=False )
  o.print_card( 'test1.png' )

  # A single US Card - Without template
  o = USBingoCard(  ) 
  o.print_card( 'test2.png' )

  # 4 US Cards - Red
  o = USBingoCard( header=90, margin_top=35, margin_left=60, margin_right=65, margin_bottom=100, with_ref_image='templates/75/red.jpg', draw_lines=False )
  BingoCard.draw_several_cards( o, how_many=4, save_to='test3.png', cols_per_image=2 )

  # 6 US Cards - Yellow 
  o = USBingoCard( header=90, margin_top=35, margin_left=60, margin_right=65, margin_bottom=100, with_ref_image='templates/75/yellow.jpg', draw_lines=False )
  BingoCard.draw_several_cards( o, how_many=6, save_to='test4.png', cols_per_image=3 )

  # A Single UK Card - Indigo
  o = UKBingoCard( header=50, margin_top=40, margin_left=35, margin_right=38, margin_bottom=42, with_ref_image='templates/90/1/indigo.jpg', draw_lines=False)
  o.print_card( 'test5.png' )

  # A Single UK Card - Blue
  o = UKBingoCard( header=50, margin_top=40, margin_left=35, margin_right=38, margin_bottom=42, with_ref_image='templates/90/1/blue.jpg', draw_lines=False)
  o.print_card( 'test5.png' )

  # A Single UK Card - Without template 
  o = UKBingoCard() 
  o.print_card( 'test6.png' )

  # A Six Set of individual cards, no unique numbers in a column - Yellow
  o = UKBingoCard( header=50, margin_top=40, margin_left=35, margin_right=38, margin_bottom=42, with_ref_image='templates/90/1/yellow.jpg', draw_lines=False)
  BingoCard.draw_several_cards( o, how_many=6, cols_per_image=1, save_to='test7.png' )


  # A Six-set UK Bingo card with unique numbers in columns - Red 
  o = UKBingoCard( set_size=6, set_gap=62.5, set_length=3, header=62.5, margin_top=1, margin_left=100, margin_right=105, margin_bottom=75, with_ref_image='templates/90/6/red.jpg', draw_lines=False)
  o.print_card( 'test8.png' )

  # A Six-set UK Bingo card with unique numbers in columns - Violet - Printed Several times
  o = UKBingoCard( set_size=6, set_gap=62.5, set_length=3, header=62.5, margin_top=1, margin_left=100, margin_right=105, margin_bottom=75, with_ref_image='templates/90/6/violet.jpg', draw_lines=False)
  BingoCard.draw_several_cards( o, how_many=6, cols_per_image=1, save_to='test9.png' )

