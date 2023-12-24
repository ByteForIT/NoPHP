use pyo3::{prelude::*, types::PyTuple};
use std::env;

fn main() -> PyResult<()> {
    let args: Vec<String> = env::args().collect();

    let py_foo = include_str!(concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/py/doodle.py"
    ));
    let py_app = include_str!(concat!(env!("CARGO_MANIFEST_DIR"), "/py/doodle.py"));
    let from_python = Python::with_gil(move |py| -> Py<PyAny> {
        PyModule::from_code(py, py_foo, "parser", "parser").unwrap();
        let app: Py<PyAny> = PyModule::from_code(py, py_app, "", "")
            .unwrap()
            .getattr("run")
            .unwrap()
            .into();
        let f1 = app.call1(py, PyTuple::new(py, vec![args[1].clone()]));

        match &f1 {
            Err(err) => {
                    println!(
                    "{}", err.traceback(py)
                    .unwrap()
                    .format()
                    .unwrap()
                );
                panic!();
            }
            Ok(_) => {
                return f1.unwrap();
            }
        };
    });

    println!("py: {}", from_python);
    Ok(())
}
