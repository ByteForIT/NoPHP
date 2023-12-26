<?php

$bootstrap = `
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN" crossorigin="anonymous">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-C6RzsynM9kWDrMNeT87bh95OGNyZPhcTNXj1NW7RuBCsyN/o0jlpcV8Qyq46cDfL" crossorigin="anonymous"></script>
`;

// Head
echo <head> $bootstrap </head>;

// Navbar
echo <nav class="navbar navbar-dark bg-dark">;
echo <a class="navbar-brand"> "NoPHP" </a>;
echo ? </nav>;

// Body
echo <body class="md-4">;

echo <div class="jumbotron">;
    echo 
         <h1 class="display-4"> "Welcome to NoPHP" </h1>
    .    <p class="lead"> "It's nice here!" </p>;
    echo <hr class="my-4">;
    echo <p> "Your lucky number is " . rand(1,100) </p>;

echo ? </div>;

echo ? </body>;


?>
