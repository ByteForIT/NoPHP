<?php
echo <html data-bs-theme="dark">;
namespace App;

require_once("example.php");

// Constant values
$bootstrap = `
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN" crossorigin="anonymous">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/default.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<!-- Select PHP and add styling -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/php.min.js"></script>
<script>hljs.highlightAll();</script>
`;
$CSS = `
.crop {
    margin: 0 auto;
    padding: 10px;
    position: relative;
}
`;

$BODY_PADDING = "md-4";
$HEAD = <head> $bootstrap . <style> $CSS </style> </head>;
$NAVBAR_ENTRIES = [
    ["Test Page", "/test"]
];
$NAVBAR = 
<nav class="navbar navbar-dark bg-dark p-2">
    <a class="navbar-brand d-flex align-items-center col-md-3 mb-2 mb-md-0 text-dark text-decoration-none"> 
        <img width=200 src="https://framerusercontent.com/images/NanQ9Rq0puTaTJZFdmoqv3WVlY.png">
    </a>

    // Append all links
    . foreach ($NAVBAR_ENTRIES as $value) {
        echo <a class="navbar-brand" href=$value[1]> $value[0] </a>
    }
</nav>;

// Head
echo $HEAD;

// Navbar
echo $NAVBAR;

// Body
$greeting = Example/greet(1);

echo 
<body class=$BODY_PADDING>
    <div class="container text-center mt-5">
        <div class="column">
            <div class="crop">
                <picture>
                  <source srcset="https://media.discordapp.net/attachments/676522094875377665/1189681029032714290/nophp-light1.png?ex=659f0bcc&is=658c96cc&hm=bafae96b4ed62e0a81bdd949f704d4bea40ab30453fd8a96b06d78eae97ce1cf&=&format=webp&quality=lossless" media="(prefers-color-scheme: dark)">null</source>
                  .<img src="https://media.discordapp.net/attachments/676522094875377665/1189672810939940874/light-removebg-preview11.png?ex=659f0425&is=658c8f25&hm=52a79c19115bfc910fa9927607a14849a0138fb96f30b5272a1138990b00b8db&=&format=webp&quality=lossless" alt="Animated wave shape">null</img>
                </picture>

                .<p class="lead"> "Nice One - PHP :: A backwards compatible language focused on modern features and flexibility." </p>
                .<hr class="my-4"> null </hr>
                // .<div class="row">
                    
                // </div>
                .<div class="row" style="text-align: start !important;">
                    <div class="col">
                        <p> "Live Debug:" </p>
                        .<p> "✓ Your lucky number is " . rand(1, 100) </p>
                        .<p> "✓ Example greeting: " . $greeting </p>
                        .<p> "✓ Greeting length: " . strlen($greeting) </p>
                        .<p> "✘ Greeting replaced (Hi -> Hello, failure when passing a function call, but passing a func name works): " .  str_replace("Hi", "Hello", $greeting) </p>
                        .<p> "✓ Substring (Hi from Example! -> from Example!): " .  substr($greeting, 2) </p>
                        .<p> "✓ Also visit the " . <a href="/test"> "testing page" </a> </p>
                        .<i style="color: green"> "✓ - Passing" </i> 
                        .<br>null</br>
                        .<i style="color: red"> "✘ - Failing" </i>
                    </div>
                    .
                    <div class="col">
                        <p> "Examples:" </p> 
                        .<pre>
                            <p> "Simple template function" </p>
                            .<code style="text-align: start !important;">
htmlspecialchars(`
function templateGreeting($name, $dash_link) {
    return <div class="greeting">
            <h1> "Welcome " . $name . "!" </h1>
            . <p> "Glad to see you again" </p>
            . <a href=$dash_link> "Go to your dashboard" </a>
           </div>;
}

echo templateGreeting("John Doe", "/dash");
`)
                            </code>
                        </pre>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>;


// ToDo: Add an empty html body parser match rule
// Footer
echo 
<footer class="fixed-bottom py-3 my-4">
    <ul class="nav justify-content-center border-bottom pb-3 mb-3">
        <li class="nav-item"><a href="#" class="nav-link px-2 text-muted"> "Home" </a></li>
        .<li class="nav-item"><a href="#" class="nav-link px-2 text-muted"> "Features" </a></li>
        .<li class="nav-item"><a href="#" class="nav-link px-2 text-muted"> "Pricing" </a></li>
        .<li class="nav-item"><a href="#" class="nav-link px-2 text-muted"> "FAQs" </a></li>
        .<li class="nav-item"><a href="#" class="nav-link px-2 text-muted"> "About" </a></li>
    </ul>
    .<p class="text-center text-muted"> "© 2023 ByteFor" </p>
</footer>;

?>
