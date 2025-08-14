import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [quiz, setQuiz] = useState({
    title: '',
    questions: [
      { question: '', options: ['', '', '', ''], answer: '' }
    ]
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setQuiz({
      ...quiz,
      [name]: value
    });
  };

  const handleQuestionChange = (index, e) => {
    const { name, value } = e.target;
    const questions = quiz.questions.map((q, i) => 
      i === index ? { ...q, [name]: value } : q
    );
    setQuiz({ ...quiz, questions });
  };

  const addQuestion = () => {
    setQuiz({
      ...quiz,
      questions: [
        ...quiz.questions,
        { question: '', options: ['', '', '', ''], answer: '' }
      ]
    });
  };

  const submitQuiz = async () => {
    try {
      const response = await axios.post('http://localhost:5000/api/quizzes', quiz);
      console.log('Quiz submitted:', response.data);
    } catch (error) {
      console.error('Error submitting quiz:', error);
    }
  };

  return (
    <div>
      <h1>Создание квиза</h1>
      <input
        type="text"
        name="title"
        value={quiz.title}
        onChange={handleInputChange}
        placeholder="Название квиза"
      />
      {quiz.questions.map((q, index) => (
        <div key={index}>
          <input
            type="text"
            name="question"
            value={q.question}
            onChange={(e) => handleQuestionChange(index, e)}
            placeholder={`Вопрос ${index + 1}`}
          />
          {q.options.map((option, optIndex) => (
            <input
              key={optIndex}
              type="text"
              name="options"
              value={option}
              onChange={(e) => {
                const options = q.options.map((o, i) => 
                  i === optIndex ? e.target.value : o
                );
                handleQuestionChange(index, { target: { name: 'options', value: options } });
              }}
              placeholder={`Вариант ${optIndex + 1}`}
            />
          ))}
          <input
            type="text"
            name="answer"
            value={q.answer}
            onChange={(e) => handleQuestionChange(index, e)}
            placeholder="Ответ"
          />
        </div>
      ))}
      <button onClick={addQuestion}>Добавить вопрос</button>
      <button onClick={submitQuiz}>Отправить квиз</button>
    </div>
  );
}

export default App;
