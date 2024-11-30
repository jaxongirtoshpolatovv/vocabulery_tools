$(document).ready(function() {
    // So'zni o'zlashtirish holatini o'zgartirish
    $('.toggle-mastery').click(function() {
        const wordId = $(this).data('word-id');
        const button = $(this);
        
        $.ajax({
            url: `/update_mastery/${wordId}`,
            method: 'POST',
            success: function(response) {
                if (response.status === 'success') {
                    if (button.hasClass('btn-warning')) {
                        button.removeClass('btn-warning').addClass('btn-success');
                        button.html('<i class="fas fa-check"></i> O\'zlashtirilgan');
                    } else {
                        button.removeClass('btn-success').addClass('btn-warning');
                        button.html('<i class="fas fa-clock"></i> O\'rganilmoqda');
                    }
                }
            }
        });
    });

    // Mashq qilish sahifasi uchun
    if ($('#practice-container').length) {
        let currentWords = [];
        let currentIndex = 0;
        
        function initializePractice() {
            currentWords = JSON.parse($('#practice-container').attr('data-words'));
            if (currentWords.length > 0) {
                shuffleArray(currentWords);
                showCurrentWord();
            }
        }

        function shuffleArray(array) {
            for (let i = array.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [array[i], array[j]] = [array[j], array[i]];
            }
        }

        function showCurrentWord() {
            const word = currentWords[currentIndex];
            $('#word-display').text(word.english);
            $('#example-display').text(word.example || '');
            $('#answer-display').text(word.uzbek);
            
            $('#answer-container').hide();
            $('#show-answer').show();
            $('#next-word').hide();
        }

        $('#show-answer').click(function() {
            $('#answer-container').slideDown();
            $(this).hide();
            $('#next-word').show();
        });

        $('#next-word').click(function() {
            currentIndex = (currentIndex + 1) % currentWords.length;
            showCurrentWord();
        });

        $('.mark-mastered, .mark-not-mastered').click(function() {
            const wordId = currentWords[currentIndex].id;
            const mastered = $(this).hasClass('mark-mastered');
            
            $.ajax({
                url: `/update_mastery/${wordId}`,
                method: 'POST',
                success: function(response) {
                    if (response.status === 'success') {
                        $('#next-word').click();
                    }
                }
            });
        });

        initializePractice();
    }
});
