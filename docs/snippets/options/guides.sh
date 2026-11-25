cat <<'EOF' | gradient - --syntax --lexer python -g --colors orange,magenta
def greet(name):
    if name:
        for _ in range(2):
            print(f'hi {name}')
EOF
