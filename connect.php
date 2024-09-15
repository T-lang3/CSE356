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
    function display_board($board, $name) {//no need to make cells interactable
        echo '<table>';
        for ($row = 0; $row < 5; $row++) {
            $row_str = get_row($board, $row);//get string of row
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
                echo "<button type='submit' name='board' style='visibility:hidden'></button>";//to take the spce that button would have taken
                continue;
            }
            $url_index = goto_index_board($board, $row, $index);
            //update url
            $new_board_str = urlencode(substr($board, 0, $url_index) . "X" . substr($board, $url_index)); // Encode spaces for the URL

            // print($new_board_str);
            //create button
            echo "<button type='submit' name='board' value='$new_board_str'>Drop</button>";
            echo '</td>';

        }
        echo '</tr></table>';
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
    function goto_index_board($board, $row, $index){
        $space = 0;
        $dot = 0;
        $pointer = 0;
        $length = strlen($board);  // Length of the board string

        while ($dot < $row && $pointer < $length){
            if ($board[$pointer] == '.') {
                $dot++;
            }
            $pointer++;
        }
        while ($space < $index && $pointer < $length) {
            if ($board[$pointer] == ' ') {
                $space++;
            }
            $pointer++;
        }
        return $pointer;
    }

    function get_row($board, $row){
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
        while($board[$right] != "." && $right < $length-1){
            $right++;
        }
        return substr($board, $left, $right-$left);
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
            $board = '1 2 3 4 5 6 7.1      .1      .1      .1      '; // 9 spaces for an empty board
        }

        echo "
        <form method='POST' class='form_box'>
        <input type='hidden' name='name' value='$name'>
        <h1>Hello, $name!</h1>
        <p>Today's date is $date.</p>
        ";
        // Display the Tic-Tac-Toe board
        // print(get_row($board, 4));
        // goto_index("c      ", index: 1);
        // print(find_inside_of_cell("1 2 3 4 5 6 ", 6) == ' ');
        // print(get_row($board, 0));
        display_drop($board, $name);
        display_board($board, $name);
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