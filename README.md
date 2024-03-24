<div align="center" style="display:grid;place-items:center;">
<p>
    <a href="https://nophp.framer.website/" target="_blank"><img width="400" src="https://framerusercontent.com/images/NanQ9Rq0puTaTJZFdmoqv3WVlY.png" alt="NoPHP"></a>
</p>
<h1>The NoPHP Language for the Modern Web</h1>
<h3>Not Only PHP - A backwards compatible language focused on modern features and flexibility.</h3>

[Official Website (WIP)](https://nophp.framer.website/) 
| [Docs](https://testing.lonk.cloud/docs) 
| [Speed (WIP)]() 
| [Contributing & compiler design](https://github.com/vlang/v/blob/master/CONTRIBUTING.md)
</div>

> [!NOTE]
> Please note, NoPHP is highly experimental and bugs are to be expected. Please create an issue on GitHub as soon as possible if you encounter any!

```php
class YourApp {
    private $greeting;
    public function __construct() {
        $this->greeting = "Welcome to NoPHP";
    } 
    public function welcome() {
        echo <h1> $this->greeting </h1>;
    }
}
$app = new YourApp();
$app->welcome();
?debug;
```

## Key Features of NoPHP
- Easily customizable language featureset
- Custom syntax for building performant code
- Write HTML directly, no headaches
- Extensive and verbose logging
- Make it your own!

## Alpha 0.2.0 and our future
Currently NoPHP is aming for a *more or less* stable release at 0.2.0. You can find the checklist [here](https://github.com/ByteForIT/NoPHP/pull/1)

NoPHP is an ongoing project and will continue to recieve updates into the far future. The purpose of this project is to provide a solution that is easy to setup for a new project or to integrate into an existing PHP codebase without massive restructuring. 

## PHP vs NoPHP
Looking at NoPHP, a question might arise in your mind: What is this for?

To answer this question simply:
NoPHP was created to solve issues that are caused by PHP being an old language
without the features most developers are used to. Some may consider this otherwise, and we fully welcome those that do to create PRs or issues with their suggestions!
The vision of this project is to create a language that is fundamentally different from PHP
while maintaining similar functionality and syntactic sugar.

Yes, Laravel exists. However their approach is different, they aim to *fix* what they
see wrong with PHP. Whilst our approach is to create what PHP was meant to be, without
sacrificing the comfort of modern languages and idioms.

## Installation
Currently NoPHP can be installed via [Pipx](https://github.com/pypa/pipx). This will only install the Python backend, others, such as the Rust backend, are a WIP. 

Below is the command needed to get started:
```bash
$ pipx install nophp
```

## Your first project
NoPHP currently provides a command to create a simple new project. It will have the basics to get you started.
```$
$ nophp -n my_cool_project
```
The command above will create a new directory named my_new_project containing the bare minimum to get you up and developing!

## Example projects
Currently available examples are few as the language is relatively new. The best ones to explore are listed below.
- [NoCMS](https://github.com/HUSKI3/NoCMS) - This is a project created for the Web Development 1 course at Inholland University of Applied Sciences. It's a simple CMS website that allows it's users to create and manage a blog. 

# Thank you to
- Kunal Dandekar - For support and aid in the Rust backend
- Vlang - For their README which was used to create this one