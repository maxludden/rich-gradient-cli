cat <<'EOF' | gradient - --syntax --lexer python --theme dracula --colors cyan,magenta
def greet(name):
    if name:
        for _ in range(2):
            print(f'hi {name}')
EOF
