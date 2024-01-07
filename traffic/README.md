# Evolution of testing

1. I used the specification from the lecture
    - filters: 32
    - dropouts: 0.5
    - layers: 128
    - kernel: 3x3
    - pool-size: 2x2
    - categories: 43

    I got as a result after 10 runs **loss:3.4973** and **accuracy: 0.056**
    Time Needed: 414ms/epoch - 1ms/step

2. I change the dropouts to 0.25 
    - filters: 32
    - dropouts: 0.25
    - layers: 128
    - kernel: 3x3
    - pool-size: 2x2
    - categories: 43

    I got as a result after 10 runs **loss:1.3939** and **accuracy: 0.5441**
    Needed Time: 429ms/epoch - 1ms/step

3. I change the hidden layer to 256
    - filters: 32
    - dropouts: 0.25
    - layers: 256
    - kernel: 3x3
    - pool-size: 2x2
    - categories: 43

     I got as a result after 10 runs **loss:0.3423** and **accuracy: 0.9126** 
     Needed Time: 470ms/epoch - 1ms/step  

4. I change the pool-size to 3x3
    - filters: 32
    - dropouts: 0.25
    - layers: 256
    - kernel: 3x3
    - pool-size: 3x3
    - categories: 43

     I got as a result after 10 runs **loss:0.2279** and **accuracy: 0.9385** 
     Needed Time: 397ms/epoch - 1ms/step 