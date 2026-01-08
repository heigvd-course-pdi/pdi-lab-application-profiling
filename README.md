Application Profiling for Performance Analysis (Java and Python)
================================================================

Learning Objectives
-------------------

In this lab, you will learn to analyze Java and Python applications to detect and locate:

1. **CPU hotspots** — where processor cycles are being consumed
2. **Memory allocation hotspots** — where memory is being allocated
3. **Memory leaks (retained memory)** — where memory accumulates and is not released
4. **Disk I/O hotspots** — where block device access occurs


We will focus on Java and Python applications using industry-standard profiling tools:
- **async-profiler** for Java CPU and I/O profiling
- **JFR (Java Flight Recorder) + JMC (JDK Mission Control)** for Java memory leak detection
- **Scalene** for Python CPU, memory, and I/O profiling

Lab Overview
------------

This lab uses two sample applications (Java and Python) that exhibit intentional performance issues. You will use profiling tools to analyze these applications and identify the root causes of their performance problems.

**Important:** Document all your findings, observations, and answers to questions in a `Report.md` file as you work through this lab.

Prerequisites
-------------

You will need a Linux system such as Ubuntu 20.04 or later with the following software installed:

1. **Java Development Kit (JDK) 21 or later**
   ```bash
   java -version
   javac -version
   ```

2. **Python 3.8 or later**
   ```bash
   python3 --version
   ```

3. **async-profiler** (for Java profiling)
   ```bash
   wget https://github.com/async-profiler/async-profiler/releases/download/v4.2.1/async-profiler-4.2.1-linux-x64.tar.gz
   tar -xzf async-profiler-4.2.1-linux-x64.tar.gz
   # Define an alias for easier access
   alias asprof="$(pwd)/async-profiler-4.2.1-linux-x64/bin/asprof"
   # Verify installation
   asprof --version
   ```

4. **JDK Mission Control (JMC)**
   ```bash
   wget https://download.java.net/java/GA/jmc9/02/binaries/jmc-9.1.1_linux-x64.tar.gz
   tar -xzf jmc-9.1.1_linux-x64.tar.gz
   # Register the path for later use
   alias jmc="$(pwd)/jmc-9.1.1_linux-x64/JDK\ Mission\ Control/jmc"
   ```

5. **Scalene** (for Python profiling)
   ```bash
   pip3 install scalene
   # Verify installation
   scalene --version
   ```

In order to run the profiling tools without root privileges, you will need to set the following kernel parameters:

```bash
sudo sysctl -w kernel.perf_event_paranoid=1
sudo sysctl -w kernel.kptr_restrict=0
```


Part 1: Java Application Profiling
----------------------------------

You can now begin profiling the Java application. async-profiler can profile CPU, memory allocations, I/O operations, and many more events, even kernel probes and syscalls. For a full list of events, see the [async-profiler documentation](https://github.com/async-profiler/async-profiler/blob/master/docs/ProfilingModes.md#perf-event-types-supported-on-linux).

There are different ways to run async-profiler. Below we will start the Java application normally and then attach async-profiler to it, using the application's process ID (PID). It is also possible to start the application with async-profiler from the beginning, but for this lab we will use the attach method.

First, navigate to the `java-app/` directory.


### Step 1.1: CPU Profiling with async-profiler

Async profiler can trace CPU usage and generate a flame graph. The flame graph visualizes which methods consume the most CPU time.

Run the following commands to profile CPU usage:

```bash
# Compile and run the Java application
javac ProfilingTarget.java;
java -Xmx512m ProfilingTarget &  
APP_PID=$!
echo "Application started with PID: $APP_PID"
sleep 3  # Wait for app to start

echo "Attach to the process for CPU Profiling..."
asprof -d 30 -f cpu-flamegraph.html $APP_PID

# Stop the application
kill $APP_PID
```

This will create a file named `cpu-flamegraph.html`, which you can open in a web browser to visualize CPU usage.

#### Understanding Flame Graphs

- **Width of bars:** Represents the amount of time spent in that function
- **Height (vertical stack):** Represents the call stack (deeper = more nested calls)
- **Color:** Just for differentiation (not meaningful in async-profiler)
- **Widest bars at the top:** These are your main targets for optimization

**Questions for Report.md:**

1. **Q1.1:** What is the widest (hottest) method in the flame graph? Take a screenshot and include it in your report.
2. **Q1.2:** What percentage of CPU time is spent in the hottest method versus other methods?


### Step 1.2: Memory Allocation Profiling with async-profiler

async-profiler can also profile memory allocations, e.g., to locate memory allocation hotspots. Let's capture memory allocation activity.

Use the same commands as before, but run the async-profiler with a different event to capture memory allocations:

```bash
... # Same as before up to starting the application
asprof -d 30 -e alloc --total -f mem-allocation-flamegraph.html $APP_PID
... # Same as before to stop the application
```

The option `--total` displays the total allocated memory in bytes, instead of just the number of allocation events.

Open `mem-allocation-flamegraph.html` in your browser.

**Questions for Report.md:**

1. **Q1.3:** Which methods are responsible for the most memory allocations? Include a screenshot.
2. **Q1.4:** How much memory (in bytes) was allocated during the 30-second profiling period?


### Step 1.3: Disk I/O Profiling with async-profiler

async-profiler can also profile Java I/O operations, e.g, to locate disk I/O hotspots. Indeed, async profiler can trace calls to any Java method, including those in the standard library. We will use this feature to trace file writes using `java.io.FileOutputStream.write` method.

Use the same commands as before, but run the async-profiler with a different event to capture call to `java.io.FileOutputStream.write`:

```bash
... # Same as before up to starting the application
asprof -d 30 -e java.io.FileOutputStream.write -f io-write-flamegraph.html $APP_PID
... # Same as before to stop the application
```

**Questions for Report.md:**

1. **Q1.5:** Which methods are responsible for most file write operations? Include a screenshot.
2. **Q1.6:** How many file read and write operations occurred during the 30-second profiling period?

<!---
```bash
# Other profiling examples you can try:
asprof -d 30 -e wall -f output.html $APP_PID # Profile wall-clock time
asprof -d 30 -e kprobe:vfs_read -f output.html $APP_PID # Profile kernel read calls
asprof -d 30 -e syscalls:sys_enter_read -f output.html $APP_PID # Profile sys_enter_read syscall
```
-->


### Step 1.4: Memory Leak Detection with JFR and JMC

Applications can have memory leaks where objects are allocated but never released, leading to increased memory usage over time. async-profiler can show allocation hotspots, but it does not directly show retained memory or leaks.

We will therefore use Java Flight Recorder (JFR) and JDK Mission Control (JMC) to detect memory leaks.

JFR is built into the JDK and can record various events, such as memory allocations and garbage collections. JMC is a GUI tool to analyze JFR recordings. 

#### Record with JFR

```bash
# Run with JFR enabled for 60 seconds
java -Xmx512m \
     -XX:+UnlockDiagnosticVMOptions \
     -XX:+DebugNonSafepoints \
     -XX:StartFlightRecording=filename=recording.jfr,dumponexit=true,settings=profile,path-to-gc-roots=true \
     ProfilingTarget
```

These options have the following effect:

- `-Xmx512m`: Limit heap size to 512 MB
- `-XX:+UnlockDiagnosticVMOptions` and `-XX:+DebugNonSafepoints`: Essential for accurate method profiling: they allow JFR to get more precise method information
- `-XX:StartFlightRecording=...`: Configures JFR to start recording immediately
- `settings=profile`: Use the "profile" settings, which include memory allocation and garbage collection events. It collects more data than the `default` settings.
- `path-to-gc-roots=true`: Enables tracking of object references to find memory leaks

Let it run for at least 60 seconds, then stop with `Ctrl+C`. This will create `recording.jfr`.

#### Analyze with JMC

JMC is a GUI application. You will therefore need a GUI environment to run it. If required, you can copy the `recording.jfr` file to your local machine and open it there. If it does not work on your Linux machine, try installing JMC on your local Windows or macOS machine. This will require JDK 21 or later installed locally.

Open the recording in JMC:

```bash
jmc recording.jfr
```

Once the window opens, click on the link "Click here to start using JDK Mission Control", if necessary.

#### Navigate JMC

1. Start with Automated Analysis Results (first page)
   - Look for any warnings or issues related to memory usage, IO, ...
   - Check the scores for different categories. High scores, colored in red, indicate potential problems. Read the descriptions for more details.

2. Analyze CPU Hotspots
   -    Navigate to Java Application page
   -    Enable only the Method Profiling checkbox on the graph
   -    Examine the Stack Trace view at the bottom
   -    Enable "Show as Tree" and "Group traces from last method frame" for better visualization. Explore the call stack tree to find CPU hotspots.
   -    Navigate to Java Application → Method Profiling for detailed view

3. Analyze Memory Allocations
   - Navigate to Java Application → Memory
   - Look at the "Allocation" and "Memory Usage" graphs in the middle
   - Look at the Class table on the top and sort it by "Total Allocation". Select the top class and check the flame graph on the bottom of the window.
   - Check the Allocation by Class tab to see which classes are allocated most
   - Navigate to Java Application → Memory → Live Objects
   - Look at the Live Object Sample table and sort it by Count to find classes that retain the most memory. These are potential memory leaks.

4. Analyze Garbage Collections
   - Navigate to Java Application → GC Summary
   - Look at the GC Pause Times and Frequency graphs to understand garbage collection behavior
   - Navigate to JVM Internals → Garbage Collections
   - Look at the GC Activity and Pause Times table to understand garbage collection behavior


**Questions for Report.md:**

1. **Q1.7:** In the "Memory" view, what trend do you observe in heap usage over time? Is it growing, stable, or decreasing? Include a screenshot.
2. **Q1.8:** Look at the "Garbage Collections" view. How often did garbage collection occur during the recording? What was the average pause time?
4. **Q1.10:** Which method is allocating most objects? (You can drill down by expanding the stack trace)
5. **Q1.11:** Which objects are not being garbage collected and are accumulating over time?



Part 2: Python Application Profiling with Scalene
-------------------------------------------------

In this part, you will profile a Python application to identify CPU hotspots, memory allocation hotspots, memory leaks, and disk I/O hotspots. Several profiling tools exist for Python, the most popular being py-spy and Scalene. Here, we will use Scalene, which can perform memory leak detection, in contrast to py-spy.

### Step 2.1: Run the Python Application

First, run the application without profiling to understand its behavior:

```bash
cd ~/python-app
python3 profiling_target.py
```

Stop it with Ctrl+C.


### Step 2.2: Profiling with Scalene

Now perform a profiling run of the application using Scalene:

```bash
scalene run profiling_target.py 200
```

Let it run for about 60 seconds, then stop with `Ctrl+C`. This will create a file named `scalene-profile.json` in the current directory.

To view the results run:

```bash
# Generate an HTML report
scalene view --html scalene-profile.json
# or open the Scalene report in your web browser
scalene view scalene-profile.json
```

The HTML report will be saved as `scalene-profile.html`, which you can open in your web browser.

The report can be confusing. In the following sections we will focus on specific issues such as CPU, memory, etc.

### Step 2.3: CPU Hotspot Analysis with Scalene

To analyze CPU usage, check the **TIME** column in the Scalene report. You can also re-run Scalene with the `--cpu-only` option to focus only on CPU profiling.

The report shows the CPU time per line (top) and per function (bottom).

**Questions for Report.md:**

1. **Q2.1:** Which function has the highest CPU usage? Include a screenshot of the Scalene report highlighting this function. Which percentage of CPU time does it consume?
2. **Q2.2:** Within this function, which specific lines have the highest CPU percentages?
4. **Q2.3:** What is the meaning of "python", "native" and "system" values in the Time column? (Hint: hover over the graphical bar in the *TIME* column))


### Step 2.4: Memory Allocation Profiling and Leak Detection with Scalene

No let's focus on memory allocation. The scalene report shows several columns related to memory allocation: peak, average, timeline, activity. The **peak** column shows the maximum memory allocated by each function or code line. The **timeline** column shows a graph of memory usage over time, which can help identify memory leaks. The **activity** column shows how the share of total memory is being allocated by each function. It may distringuish between Python and native memory allocations.

**Questions for Report.md:**

1. **Q2.4:** Which function and code line shows the highest memory allocation? Include a screenshot.
2. **Q2.5:** Is the memory allocation stable over time, or does it increase continuously (indicating a memory leak)?
3. **Q2.6:** On the top of the report, is the Memory Timeline increasing or does it go down from time to time? What does it mean if the memory allocation goes down?


### Step 2.5: Disk I/O Analysis with Scalene

Scalene does not directly show disk I/O hotspots, but I/O-heavy operations can be inferred from the **TIME** column. If you hover over the graphical bar in the **TIME** column, you can see the breakdown of time spent in Python code, native code, and system calls. High system time may indicate I/O operations.

**Questions for Report.md:**

1. **Q2.7:** Which function performs the most disk I/O operations? Does it show high system time in the TIME column? Include a screenshot.
2. **Q2.8:** Within this function, which specific line has the highest system time percentage?

Conclusion
----------

In this lab, you have learned to profile Java and Python applications using async-profiler, JFR/JMC, and Scalene. You have identified CPU hotspots, memory allocation hotspots, memory leaks, and disk I/O hotspots in both applications.

While you many not use these exact tools in your daily work, the concepts and techniques learned here are applicable to a wide range of performance analysis tasks. In particular, interpreting flame graphs, memory allocation profiles, and understanding memory leaks are essential skills for any performance engineer or developer.
