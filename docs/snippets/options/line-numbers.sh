cat <<'EOF' | gradient - --syntax --lexer python -n --colors lime,cyan
def greet(name):
    if name:
        for _ in range(2):
            print(f'hi {name}')
EOF
