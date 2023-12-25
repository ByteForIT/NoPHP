use pyo3::{prelude::*, types::PyTuple};
use pythonize::depythonize;
use serde_json::Value;
use std::{env, error::Error};

fn main() -> PyResult<()> {
    let args: Vec<String> = env::args().collect();

    let py_foo = include_str!(concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/py/doodle.py"
    ));
    let py_app = include_str!(concat!(env!("CARGO_MANIFEST_DIR"), "/py/doodle.py"));
    let from_python = Python::with_gil(move |py| -> Value {
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
                let obj = f1.unwrap();

                let serialised : Value = depythonize(obj.to_object(py).as_ref(py)).unwrap();

                return serialised;
            }
        };
    });

    let vecc = gyattttt(from_python).unwrap();

    println!("py: {}", vecc[0]);
    Ok(())
}

fn gyattttt(from_python: Value) -> Option<Vec<Value>> {
    let vecc : &Vec<Value> = from_python.as_array()?;
    let vecc : &Vec<Value> = vecc[0].as_array()?;

    return Some(vecc.to_vec());
}
