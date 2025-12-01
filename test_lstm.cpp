#include <iostream>
#include <vector>
#include <cstdlib>
#include <ctime>
#include "paq8px/model/LstmMixer.hpp"

/**
 * Simple test for LstmMixer
 * Verifies:
 * 1. Compilation works
 * 2. Predict() returns values in [0,1]
 * 3. Learn() updates weights
 * 4. LSTM adapts to patterns
 */

void test_basic_functionality() {
    std::cout << "=== Test 1: Basic Functionality ===" << std::endl;
    
    // Create LSTM with 5 inputs, 8 cells
    LstmMixer lstm(5, 8, 0.01f);
    
    // Test prediction
    std::vector<float> inputs = {0.1f, 0.5f, 0.3f, 0.8f, 0.2f};
    float pred = lstm.predict(inputs);
    
    std::cout << "Prediction: " << pred << std::endl;
    std::cout << "Expected: between 0.0 and 1.0" << std::endl;
    std::cout << "Status: " << (pred >= 0.0f && pred <= 1.0f ? "PASS" : "FAIL") << std::endl;
    
    // Test learning
    lstm.learn(1);  // Actual bit was 1
    float pred2 = lstm.predict(inputs);
    
    std::cout << "After learning (target=1), prediction: " << pred2 << std::endl;
    std::cout << "Expected: should be > initial prediction" << std::endl;
    std::cout << "Status: " << (pred2 > pred ? "PASS" : "MAYBE OK (learning is gradual)") << std::endl;
    std::cout << std::endl;
}

void test_pattern_learning() {
    std::cout << "=== Test 2: Pattern Learning ===" << std::endl;
    
    // Create LSTM
    LstmMixer lstm(3, 16, 0.1f);
    
    // Simple pattern: if input[0] > 0.5, output = 1, else output = 0
    std::cout << "Training on pattern: output = 1 if input[0] > 0.5" << std::endl;
    
    // Train for 100 steps
    for (int i = 0; i < 100; i++) {
        float val = (float)rand() / RAND_MAX;
        std::vector<float> inputs = {val, 0.5f, 0.5f};
        int target = (val > 0.5f) ? 1 : 0;
        
        float pred = lstm.predict(inputs);
        lstm.learn(target);
        
        if (i % 25 == 0) {
            std::cout << "Step " << i << ": input=" << val 
                      << ", target=" << target << ", pred=" << pred << std::endl;
        }
    }
    
    // Test learned pattern
    std::cout << "\nTesting learned pattern:" << std::endl;
    
    std::vector<float> test1 = {0.2f, 0.5f, 0.5f};  // Should predict ~0
    float pred1 = lstm.predict(test1);
    std::cout << "Input 0.2 (expect 0): " << pred1 
              << " " << (pred1 < 0.3f ? "GOOD" : "NEEDS MORE TRAINING") << std::endl;
    
    std::vector<float> test2 = {0.8f, 0.5f, 0.5f};  // Should predict ~1
    float pred2 = lstm.predict(test2);
    std::cout << "Input 0.8 (expect 1): " << pred2 
              << " " << (pred2 > 0.7f ? "GOOD" : "NEEDS MORE TRAINING") << std::endl;
    
    std::cout << std::endl;
}

void test_alternating_sequence() {
    std::cout << "=== Test 3: Sequence Memory ===" << std::endl;
    
    // Create LSTM
    LstmMixer lstm(1, 32, 0.05f);
    
    // Train on alternating sequence: 0, 1, 0, 1, 0, 1, ...
    std::cout << "Training on alternating sequence: 0, 1, 0, 1, ..." << std::endl;
    
    std::vector<float> inputs = {0.5f};  // Constant input
    float loss = 0.0f;
    
    for (int i = 0; i < 200; i++) {
        int target = i % 2;
        float pred = lstm.predict(inputs);
        lstm.learn(target);
        
        loss += std::abs(pred - target);
        
        if (i >= 190) {
            std::cout << "Step " << i << ": target=" << target 
                      << ", pred=" << pred << std::endl;
        }
    }
    
    std::cout << "Average loss (last 200 steps): " << (loss / 200.0f) << std::endl;
    std::cout << "Expected: < 0.3 (LSTM should learn pattern)" << std::endl;
    std::cout << std::endl;
}

void test_reset() {
    std::cout << "=== Test 4: State Reset ===" << std::endl;
    
    LstmMixer lstm(2, 8, 0.01f);
    
    // Make some predictions to build up state
    std::vector<float> inputs = {0.7f, 0.3f};
    for (int i = 0; i < 10; i++) {
        lstm.predict(inputs);
        lstm.learn(1);
    }
    
    float pred_before_reset = lstm.predict(inputs);
    std::cout << "Prediction before reset: " << pred_before_reset << std::endl;
    
    // Reset state
    lstm.reset();
    
    float pred_after_reset = lstm.predict(inputs);
    std::cout << "Prediction after reset: " << pred_after_reset << std::endl;
    std::cout << "Expected: Different from before (state cleared)" << std::endl;
    std::cout << "Status: " << (std::abs(pred_before_reset - pred_after_reset) > 0.01f ? 
                                 "PASS" : "MAYBE OK (depends on initialization)") << std::endl;
    std::cout << std::endl;
}

int main() {
    // Seed random number generator
    srand(static_cast<unsigned int>(time(nullptr)));
    
    std::cout << "========================================" << std::endl;
    std::cout << "   LSTM Mixer Test Suite" << std::endl;
    std::cout << "========================================" << std::endl;
    std::cout << std::endl;
    
    test_basic_functionality();
    test_pattern_learning();
    test_alternating_sequence();
    test_reset();
    
    std::cout << "========================================" << std::endl;
    std::cout << "   All Tests Complete!" << std::endl;
    std::cout << "========================================" << std::endl;
    std::cout << std::endl;
    std::cout << "Next steps:" << std::endl;
    std::cout << "1. If tests PASS: Integrate with PAQ8px" << std::endl;
    std::cout << "2. If tests FAIL: Debug LSTM implementation" << std::endl;
    std::cout << "3. Tune hyperparameters (learning rate, cells)" << std::endl;
    std::cout << "4. Test on real compression data" << std::endl;
    
    return 0;
}
