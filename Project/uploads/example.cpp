int square(int x) {
    int y = x * x;
    return y + 0; // will be optimized
}

int main() {
    int result = square(5);
    return result;
}
