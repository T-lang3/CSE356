<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connect4</title>
    <link rel="stylesheet" href="connect.css"> <!-- Link to the CSS file -->
</head>
<body>
    <?php
    //oponnet randomize columns chosen. See if it's placeable, if not go to next column.
    function display_board($board, $name) {//no need to make cells interactable
        echo '<table>';
        for ($row = 0; $row < 5; $row++) {
            $row_str = get_row($board, $row);//get string of row     get row for last row isn't getting the last cell
            // print($row_str);
            echo '<tr>';
            for ($col = 0; $col < 7; $col++) {//get the correct row, add in the x, replace the row in the overall board.
                $cell = find_inside_of_cell($row_str, $col);//get col index character of row
                echo "<td>$cell</td>";
            }
            echo '</tr>';
        }
        echo '</table>';
    }

    function display_drop($board, $name) {//for each row, find if index is occupied, if yes go to row-1
        echo '<table><tr>';
        //for each column, if the second row is not open, then if X is placed, O can't be in the same column
        for ($index = 0; $index < 7; $index++) {
            echo '<td>';
            //find index for new x
            $row = 4;
            while ($row != -1){
                $row_str = get_row($board, $row);
                // print($row_str);
                // print(strlen($row_str));
                if (find_inside_of_cell($row_str, $index) != ' '){//if true, then there is something there so we should go to previous row, otherwise we exit
                    $row--;
                }
                else{
                    break;
                }
            }
            // print($row);
            if ($row == -1){
                // echo "<button type='submit' name='board' style='visibility:hidden'></button>";//to take the space that button would have taken
                echo '';
                continue;
            }
            $opponent_url = opponent_move($board, $index);
            $url_index = goto_index_board($board, $row, $index);
            //update url
            if ($opponent_url == -1){//there is no opponent move
                $new_board_str = urlencode(substr($board, 0, $url_index) . "X" . substr($board, $url_index)); // Encode spaces for the URL
            }
            else{
                if ($url_index > $opponent_url){//O then X
                    $new_board_str = urlencode(substr($board, 0, $opponent_url) . "O" .
                        substr($board, $opponent_url, $url_index - $opponent_url) . "X" .
                        substr($board, $url_index)
                    ); // Encode spaces for the URL
                }
                else {//X then O
                    $new_board_str = urlencode(substr($board, 0, $url_index) . "X" .
                        substr($board, $url_index, $opponent_url - $url_index) . "O" .
                        substr($board, $opponent_url)
                    ); // Encode spaces for the URL
                }
            }
            // print($new_board_str);
            //create button
            echo "<button type='submit' name='board' value='$new_board_str'>Drop</button>";
            echo '</td>';

        }
        echo '</tr></table>';
    }

    function get_col_open_in_row($board, $index){//gets the open cells in a row
        $moves = [];
        $pointer = 0;
        // print($index. "jk");
        $row = get_row($board, $index);//get row
        $length = strlen($row);  // Length of the board string
        // print($row);
        for ($i = 0; $i < 6; $i++){

            //print($row[$pointer]);
            if ($row[$pointer] == ' '){//there is a move here
                $moves[] = $i;
                $pointer++;
                continue;
            }
            else if ($pointer < $length && $row[$pointer] != ' ') {
                $pointer+=2;
            }
        }
        // print($pointer. "len: " .$length);
        if ($pointer == $length && $row[$pointer-1] == " "){
            $moves[] = 6;
        }
        return $moves;
    }

    function opponent_move($board, $index){//returns the place in the url where opponent will place its move
        $first = get_col_open_in_row($board, 0);//get topmost row
        if (count($first) == 0) {//no moves for opponent
            return -1;
        }
        foreach ($first as $cell) {//search through free cols. if cell matches index, opponent is putting his move there, so row--
            //find index for new x
            $row = 4;
            while ($row != -1){
                $row_str = get_row($board, $row);
                // print($row_str);
                // print(strlen($row_str));
                if (find_inside_of_cell($row_str, $cell) != ' '){//if true, then there is something there so we should go to previous row, otherwise we exit
                    $row--;
                }
                else{
                    break;
                }
            }
            if ($index == $cell){
                $row--;
            }
            if ($row != -1){//found the row where the opponent can place it.
                return goto_index_board($board, $row, $cell);
            }
        }
        return -1;
    }

    function find_inside_of_cell($str, $index){//get row first, then col of row
        $space = 0;
        $pointer = 0;
        $length = strlen($str);  // Length of the board string
        while ($space < $index && $pointer < $length) {
            if ($str[$pointer] == ' ') {
                $space++;
            }
            $pointer++;
        }
        if ($pointer == $length){
            return " ";
        }
        return $str[$pointer];
    }

    function convert_to_array($board){
        $array = [];
        for ($i = 0; $i < 5; $i++){
            $array[$i] = [];
        }
        for ($i = 0; $i < 5; $i++){
            $str = get_row($board, $i);
            $pointer = 0;
            for ($j = 0; $j < 6; $j++){
                $array[$i][$j] = $str[$pointer];
                //print($row[$pointer]);
                if ($str[$pointer] == ' '){//there is a move here
                    $pointer++;
                }
                else{
                    $pointer+=2;
                }
            }
            if ($pointer == strlen($str) && $str[$pointer-1] == " "){
                $array[$i][6] = " ";
            }
            else{
            	$array[$i][6] = $str[$pointer];
            }
        }
        return $array;
    }
    function goto_index_board($board, $row, $index){
        $space = 0;
        $dot = 0;
        $pointer = 0;
        $length = strlen($board);  // Length of the board string

        while ($dot < $row && $pointer < $length){//advance through the rows
            if ($board[$pointer] == '.') {
                $dot++;
            }
            $pointer++;
        }
        while ($space < $index && $pointer < $length) {//advance through the cols
            if ($board[$pointer] == ' ') {
                $space++;
            }
            $pointer++;
        }
        if ($pointer == $length && $board[$pointer-1] == " "){
            // $pointer--;
        }
        return $pointer;
    }

    function get_row($board, $row){
        if ($row > 4){
            print("Error, why is row more than index: 4");
            return;
        }
        $dot = 0;
        $left = 0;
        $length = strlen($board);  // Length of the board string

        while ($dot < $row){
            if ($board[$left] == '.') {
                $dot++;
            }
            $left++;
        }
        $right = $left;
        while($right < $length && $board[$right] != "."){
            $right++;
        }
        return substr($board, $left, $right-$left);
    }

    function check_winner($board) {
        // print("a".$board."b");
        // Winning combinations
        $cols = 7;
        $rows = 5;
        $array = convert_to_array($board);
        for ($row = 0; $row < $rows; $row++) {
            for ($col = 0; $col < $cols; $col++) {
                $current = $array[$row][$col];
                if ($current == 'X') { // Check for your win first
                    // Check horizontal
                    if ($col + 3 < $cols &&
                        $current === $array[$row][$col + 1] &&
                        $current === $array[$row][$col + 2] &&
                        $current === $array[$row][$col + 3]) {
                        return $current; // Winner found
                    }
    
                    // Check vertical
                    if ($row + 3 < $rows &&
                        $current === $array[$row + 1][$col] &&
                        $current === $array[$row + 2][$col] &&
                        $current === $array[$row + 3][$col]) {
                        return $current; // Winner found
                    }
    
                    // Check diagonal (down-right)
                    if ($row + 3 < $rows && $col + 3 < $cols &&
                        $current === $array[$row + 1][$col + 1] &&
                        $current === $array[$row + 2][$col + 2] &&
                        $current === $array[$row + 3][$col + 3]) {
                        return $current; // Winner found
                    }
    
                    // Check diagonal (up-right)
                    if ($row - 3 >= 0 && $col + 3 < $cols &&
                        $current === $array[$row - 1][$col + 1] &&
                        $current === $array[$row - 2][$col + 2] &&
                        $current === $array[$row - 3][$col + 3]) {
                        return $current; // Winner found
                    }
                }
            }
        }
        for ($row = 0; $row < $rows; $row++) {
            for ($col = 0; $col < $cols; $col++) {
                $current = $array[$row][$col];
                if ($current == 'O') { // Check for their win second
                    // Check horizontal
                    if ($col + 3 < $cols &&
                        $current === $array[$row][$col + 1] &&
                        $current === $array[$row][$col + 2] &&
                        $current === $array[$row][$col + 3]) {
                        return $current; // Winner found
                    }
    
                    // Check vertical
                    if ($row + 3 < $rows &&
                        $current === $array[$row + 1][$col] &&
                        $current === $array[$row + 2][$col] &&
                        $current === $array[$row + 3][$col]) {
                        return $current; // Winner found
                    }
    
                    // Check diagonal (down-right)
                    if ($row + 3 < $rows && $col + 3 < $cols &&
                        $current === $array[$row + 1][$col + 1] &&
                        $current === $array[$row + 2][$col + 2] &&
                        $current === $array[$row + 3][$col + 3]) {
                        return $current; // Winner found
                    }
    
                    // Check diagonal (up-right)
                    if ($row - 3 >= 0 && $col + 3 < $cols &&
                        $current === $array[$row - 1][$col + 1] &&
                        $current === $array[$row - 2][$col + 2] &&
                        $current === $array[$row - 3][$col + 3]) {
                        return $current; // Winner found
                    }
                }
            }
        }
    
        // Check for a draw (no empty spaces)
        if (count(get_col_open_in_row($board, 0)) == 0) {
            return 'Draw';
        }
    
        // Game is still ongoing
        return null;
    }

    // Check if 'name' is present in the GET request
    if (isset($_POST['name']) && !empty($_POST['name'])) {
        // Get the 'name' from the POST data
        $name = htmlspecialchars($_POST['name']); // Sanitize for security
        // Get the current date
        date_default_timezone_set('America/New_York');
        $date = date('m/d/y, h:i A'); // Example: "Saturday, September 14, 2024"

        if (isset($_POST['board'])) {
            $board = urldecode($_POST['board']); // Decode URL encoding

        } else {
            $board = '      .      .      .      .      '; // 6 spaces per row
        }

        echo "
        <form method='POST' class='form_box'>
        <input type='hidden' name='name' value='$name'>
        <h1>Hello, $name!</h1>
        <p>Today's date is $date.</p>
        ";
        // $array = convert_to_array($board);
        // print(json_encode($array));
        if (check_winner($board) == "X") {
            echo "
                <p>You won!</p>
                <form method='POST' action='connect.php'>
                    <input type='hidden' name='name' value='$name'>
                    <button type='submit'>Play again</button>
                </form>
            ";
        }
        else if (check_winner($board) == "O") {
            echo "
                <p>I won!</p>
                <form method='POST' action='connect.php'>
                    <input type='hidden' name='name' value='$name'>
                    <button type='submit'>Play again</button>
                </form>
            ";
        }
        else if (check_winner($board) == "Draw") {
            echo '
                Draw
            ';
        }
        else{
            display_drop($board, $name);
            display_board($board, $name);
        }
        echo '</form>';
    } else {
        // If 'name' is not provided, display the form
        echo '
        <div class="form_box">
        <h1>Welcome to Connect 4!</h1>
        <form method="POST" action="connect.php" class="box">
            <label for="name" >Enter your name:</label>
            <input type="text" id="name" name="name" required>
            <input type="submit" value="Submit">
        </form>
        </div>
        ';
    }
    ?>
</body>
</html>