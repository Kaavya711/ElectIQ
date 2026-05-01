document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('start-quiz-btn');
    const startScreen = document.getElementById('quiz-start-screen');
    const questionScreen = document.getElementById('quiz-question-screen');
    const resultScreen = document.getElementById('quiz-result-screen');
    
    let currentQuizData = null;
    let currentQuestionIndex = 0;
    let userAnswers = [];
    
    const countryCode = document.querySelector('meta[name="country_code"]')?.content || 'IN';

    if (startBtn) {
        startBtn.addEventListener('click', async () => {
            startBtn.textContent = 'Generating Quiz...';
            startBtn.disabled = true;
            
            try {
                const response = await fetch('/api/generate-quiz', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ country: countryCode })
                });
                const data = await response.json();
                
                if (data.error || (data[0] && data[0].error)) {
                    alert('Quiz generation failed. Using fallback.');
                    // In a real app we'd fall back more gracefully. 
                    // Assuming the backend handles fallback for us.
                }
                
                currentQuizData = data;
                userAnswers = [];
                currentQuestionIndex = 0;
                
                startScreen.classList.add('hidden');
                questionScreen.classList.remove('hidden');
                
                renderQuestion();
            } catch (error) {
                console.error("Quiz start error:", error);
                startBtn.textContent = 'Start Quiz →';
                startBtn.disabled = false;
                alert("Could not start quiz. Please try again.");
            }
        });
    }

    function renderQuestion() {
        if (!currentQuizData || currentQuestionIndex >= currentQuizData.length) {
            submitQuiz();
            return;
        }

        const q = currentQuizData[currentQuestionIndex];
        
        // Update progress
        document.getElementById('quiz-progress-text').textContent = `${currentQuestionIndex + 1} / ${currentQuizData.length}`;
        document.getElementById('quiz-progress-fill').style.width = `${((currentQuestionIndex) / currentQuizData.length) * 100}%`;
        
        document.getElementById('quiz-question-text').textContent = q.question;
        
        const optionsContainer = document.getElementById('quiz-options-container');
        optionsContainer.innerHTML = '';
        
        q.options.forEach((opt, idx) => {
            const btn = document.createElement('button');
            btn.className = 'quiz-option';
            btn.textContent = opt;
            btn.onclick = () => handleAnswerSelect(idx, btn);
            optionsContainer.appendChild(btn);
        });

        document.getElementById('quiz-explanation').style.display = 'none';
        
        const nextBtn = document.getElementById('quiz-next-btn');
        nextBtn.style.display = 'none';
        nextBtn.onclick = () => {
            currentQuestionIndex++;
            renderQuestion();
        };
    }

    function handleAnswerSelect(selectedIndex, btnElement) {
        const q = currentQuizData[currentQuestionIndex];
        userAnswers.push(selectedIndex);
        
        const isCorrect = selectedIndex === q.correct;
        
        // Disable all options
        const allBtns = document.querySelectorAll('.quiz-option');
        allBtns.forEach((btn, idx) => {
            btn.disabled = true;
            if (idx === q.correct) {
                btn.classList.add('correct');
                if (idx !== selectedIndex) {
                    btn.innerHTML += ' (Correct Answer)';
                }
            } else if (idx === selectedIndex && !isCorrect) {
                btn.classList.add('wrong');
                btn.innerHTML += ' ✗ Incorrect';
            }
        });

        if (isCorrect) {
            btnElement.innerHTML += ' ✓ Correct!';
        }

        // Show explanation
        const explanationEl = document.getElementById('quiz-explanation');
        explanationEl.textContent = q.explanation;
        explanationEl.style.display = 'block';

        // Show next button
        const nextBtn = document.getElementById('quiz-next-btn');
        if (currentQuestionIndex === currentQuizData.length - 1) {
            nextBtn.textContent = 'See Results →';
        } else {
            nextBtn.textContent = 'Next Question →';
        }
        nextBtn.style.display = 'inline-block';
    }

    async function submitQuiz() {
        questionScreen.classList.add('hidden');
        
        try {
            const response = await fetch('/api/submit-quiz', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ answers: userAnswers })
            });
            const data = await response.json();
            
            showResults(data);
        } catch(error) {
            console.error("Failed to submit", error);
            alert("Failed to calculate results.");
        }
    }

    function showResults(data) {
        resultScreen.classList.remove('hidden');
        
        document.getElementById('result-score-text').textContent = `${data.score} / ${data.total}`;
        
        const badgeEl = document.getElementById('result-badge');
        const ratio = data.score / data.total;
        if (ratio === 1) badgeEl.textContent = "🏆 Election Expert!";
        else if (ratio >= 0.8) badgeEl.textContent = "🌟 Excellent!";
        else if (ratio >= 0.6) badgeEl.textContent = "👍 Good Work!";
        else if (ratio >= 0.4) badgeEl.textContent = "📚 Keep Learning!";
        else badgeEl.textContent = "🗳️ Just Getting Started!";

        const breakdownContainer = document.getElementById('result-breakdown');
        breakdownContainer.innerHTML = '';

        data.results.forEach((res, i) => {
            const div = document.createElement('div');
            div.className = 'breakdown-item';
            div.innerHTML = `
                <p><strong>Q${i+1}:</strong> ${res.question}</p>
                <p style="color: ${res.is_correct ? '#4CAF50' : '#F44336'}">
                    Your answer: ${res.user_answer} ${res.is_correct ? '✓' : '✗'}
                </p>
                ${!res.is_correct ? `<p style="color: #4CAF50">Correct answer: ${res.correct_answer}</p>` : ''}
                <p class="muted" style="font-size: 14px; margin-top: 8px;">${res.explanation}</p>
            `;
            breakdownContainer.appendChild(div);
        });
    }

    const retryBtn = document.getElementById('retry-btn');
    if (retryBtn) {
        retryBtn.addEventListener('click', () => {
            resultScreen.classList.add('hidden');
            startScreen.classList.remove('hidden');
            startBtn.textContent = 'Start Quiz →';
            startBtn.disabled = false;
        });
    }
});
