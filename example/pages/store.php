<?php
namespace Shop;

echo
<form action="/store" method="post">
<input type="submit" value="POST"> null </input> 
</form>;

echo
<form action="/store" method="get">
<input type="submit" value="GET">null</input> 
</form>;

if ($_SERVER["method"] == "POST") {
    echo "Got post!";
} else {
    echo "Got get!";
}
?>