#!/bin/bash


choices=("rock" "paper" "scissors")

echo "✊ ✋ ✌ Welcome to Rock, Paper, Scissors!"
read -p "Enter and choose (rock, paper, scissors): " player_choice

# Convert to lowercase
player_choice=$(echo "$player_choice" | tr '[:upper:]' '[:lower:]')

# Check for valid input
if [[ ! " ${choices[@]} " =~ " $player_choice " ]]; then
    echo "❌ Invalid choice! Choose rock, paper, or scissors."
    read -p "Enter and choose (rock, paper, scissors): " player_choice
    #exit 1
fi

running=true

while [ "$running" = true ]; do
    # Computer randomly selects
    computer_choice=${choices[$RANDOM % 3]}
    echo "🤖 Computer chose: $computer_choice"

    # Display player's and computer's choices
    echo "Player: $player_choice"
    echo "Computer: $computer_choice"

    # Determine the winner
    if [ "$player_choice" = "$computer_choice" ]; then
        echo "🤝 It's a tie!"
    elif [ "$player_choice" = "rock" ] && [ "$computer_choice" = "scissors" ]; then
        echo "🎉 You win! Rock beats Scissors."
    elif [ "$player_choice" = "paper" ] && [ "$computer_choice" = "rock" ]; then
        echo "🎉 You win! Paper beats Rock."
    elif [ "$player_choice" = "scissors" ] && [ "$computer_choice" = "paper" ]; then
        echo "🎉 You win! Scissors beats Paper."
    else
        echo "😢 You lose! Better luck next time."
    fi

    # Ask if the player wants to play again
    read -p "Do you want to play again? (yes/no): " play_again
    if [ "$play_again" != "yes" ]; then
        running=false
        echo "Thanks for playing! Goodbye!"
    else
        read -p "Enter and choose (rock, paper, scissors): " player_choice
        # Convert to lowercase again for the next round
        player_choice=$(echo "$player_choice" | tr '[:upper:]' '[:lower:]')
        # Check for valid input
        if [[ ! " ${choices[@]} " =~ " $player_choice " ]]; then
            echo "❌ Invalid choice! Choose rock, paper, or scissors."
            read -p "Enter and choose (rock, paper, scissors): " player_choice

            
            #exit 1
        fi
    fi
done

chmod +x Rock_Paper_Scissors_Game.sh

