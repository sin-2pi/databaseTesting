use rusqlite::{Connection, Result};
use std::collections::HashMap;
use std::io::{self, Write};
use std::process;

fn main() -> Result<()> {
    let mut possible_queries = HashMap::new();

    possible_queries.insert("1".to_string(), "All students in a class".to_string());
    possible_queries.insert("2".to_string(), "All students for a teacher".to_string());
    possible_queries.insert("3".to_string(), "All students in a class with the teacher".to_string());
    // Paste full path to 'enrollment.db' here
    let connection = Connection::open("!!!paste path here!!!")?;
    loop {
        let user_query_choice = display_choices(&possible_queries);

        if user_query_choice == "1" {
            run_course_query(&connection, &possible_queries, &user_query_choice)?;
        }

        if user_query_choice == "2" {
            query_students_for_teacher(&connection, &possible_queries, &user_query_choice)?;
        }

        if user_query_choice == "3" {
            query_students_in_class_with_teacher(&connection, &possible_queries, &user_query_choice)?;
        }
    }
}

fn display_choices<V>(choice_map: &HashMap<String, V>) -> String {
    print!(
    "--- Available Queries ---\n\
    1 - All students in a class\n\
    2 - All students for a teacher\n\
    3 - All students in a class with a teacher\n\
    'exit' to exit\n\
    Selection: "
    );

    io::stdout().flush().unwrap();

    let mut user_choice = String::new();
    io::stdin()
        .read_line(&mut user_choice)
        .expect("Failed to read line");
    let user_choice = user_choice.trim().to_string();

    if user_choice.to_lowercase() == "exit" {
        process::exit(0);
    }

    if choice_map.contains_key(&user_choice) {
        user_choice
    } else {
        println!("Invalid selection.");
        return display_choices(choice_map);
    }
}

fn run_course_query(
    connection: &Connection,
    possible_queries: &HashMap<String, String>,
    user_query_choice: &str,
) -> Result<()> {
    print!("Enter course ID: ");
    io::stdout().flush().unwrap();

    let mut input_id = String::new();
    let _ = io::stdin().read_line(&mut input_id);
    let input_id = input_id.trim().to_string();

    if input_id.to_lowercase() == "exit" {
        process::exit(0);
    }
    let mut stmt = connection.prepare(
        "SELECT Students.student_name
         FROM Students
         INNER JOIN Enrollment ON Students.student_id = Enrollment.student_id
         WHERE Enrollment.course_id = ?1;",
    )?;

    let students_iter = stmt.query_map([&input_id], |row| {
        let name: String = row.get(0)?;
        Ok(name)
    })?;

    let mut name_query = connection.prepare(
        "SELECT course_name
         FROM Courses
         WHERE course_id = ?;",
    )?;

    let course_name: String = name_query.query_row([&input_id], |row| {
        let course_name: String = row.get(0)?;
        Ok(course_name)
    })?;

    println!(
        "--- {}: '{}' --- ",
        possible_queries
            .get(user_query_choice)
            .unwrap(),
        course_name
    );

    for student_result in students_iter {
        println!("{}", student_result?);
    }
    println!("\n");

    Ok(())
}

fn query_students_for_teacher(
    connection: &Connection,
    possible_queries: &HashMap<String, String>,
    user_query_choice: &str,
) -> Result<()> {
    print!("Enter teacher ID: ");
    io::stdout().flush().unwrap();

    let mut input_id = String::new();
    let _ = io::stdin().read_line(&mut input_id);
    let input_id = input_id.trim().to_string();

    if input_id.to_lowercase() == "exit" {
        process::exit(0);
    }

    let mut stmt = connection.prepare(
        "SELECT DISTINCT Students.student_id, Students.student_name
         FROM Students
         JOIN Enrollment ON Students.student_id = Enrollment.student_id
         JOIN Courses ON Enrollment.course_id = Courses.course_id
         WHERE Courses.teacher_id = ?1;",
    )?;

    let students_iter = stmt.query_map([&input_id], |row| {
        let name: String = row.get(1)?;
        Ok(name)
    })?;

    let mut name_query = connection.prepare(
        "SELECT teacher_name
         FROM Teachers
         WHERE teacher_id = ?;",
    )?;

    let teacher_name: String = name_query.query_row([&input_id], |row| {
        let name: String = row.get(0)?;
        Ok(name)
    })?;

    println!(
        "--- {}: '{}' --- ",
        possible_queries
            .get(user_query_choice)
            .unwrap(),
        teacher_name
    );

    for student_result in students_iter {
        println!("{}", student_result?);
    }
    println!("\n");

    Ok(())
}

fn query_students_in_class_with_teacher(
    connection: &Connection,
    possible_queries: &HashMap<String, String>,
    user_query_choice: &str,
) -> Result<()> {
    print!("Enter course ID: ");
    io::stdout().flush().unwrap();

    let mut input_id = String::new();
    let _ = io::stdin().read_line(&mut input_id);
    let input_id = input_id.trim().to_string();

    if input_id.to_lowercase() == "exit" {
        process::exit(0);
    }
    let mut stmt = connection.prepare(
        "SELECT Students.student_id, Students.student_name, Teachers.teacher_name
         FROM Students
         JOIN Enrollment ON Students.student_id = Enrollment.student_id
         JOIN Courses ON Enrollment.course_id = Courses.course_id
         JOIN Teachers ON Courses.teacher_id = Teachers.teacher_id
         WHERE Enrollment.course_id = ?1;",
    )?;

    let students_iter = stmt.query_map([&input_id], |row| {
        let name: String = row.get(1)?;
        Ok(name)
    })?;

    let mut name_query = connection.prepare(
        "SELECT Courses.course_name, Teachers.teacher_name
         FROM Courses
         JOIN Teachers ON Courses.teacher_id = Teachers.teacher_id
         WHERE Courses.course_id = ?;",
    )?;

    let (course_name, teacher_name): (String, String) =
        name_query.query_row([&input_id], |row| {
            let course_name: String = row.get(0)?;
            let teacher_name: String = row.get(1)?;
            Ok((course_name, teacher_name))
        })?;

    println!(
        "--- {} --- '{}' with '{}'",
        possible_queries
            .get(user_query_choice)
            .unwrap(),
        course_name,
        teacher_name
    );

    for student_result in students_iter {
        match student_result {
            Ok(student_name) => println!("{}", student_name),
            Err(e) => {
                eprintln!("Error retrieving student: {}", e);
                return Ok(());
            }
        }
    }
    println!("\n");

    Ok(())
}
