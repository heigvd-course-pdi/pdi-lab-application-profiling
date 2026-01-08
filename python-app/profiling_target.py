#!/usr/bin/env python3
"""
profiling_target.py - A Python application with intentional performance issues
for students to discover using Scalene profiler.

Issues to find:
1. CPU Hotspot: Inefficient prime number calculation
2. CPU Hotspot: Unnecessary string concatenation in loop
3. Memory Leak: Objects retained in a list that grows indefinitely
4. Memory Allocation Hotspot: Creating many temporary objects
5. Disk I/O Hotspot: Synchronous file writes without buffering
6. Disk I/O Hotspot: Reading files byte-by-byte
"""

import os
import sys
import time
import tempfile
import hashlib
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import numpy as np

# MEMORY LEAK: Global list that accumulates objects and is never cleared
leaky_cache: List['LeakyObject'] = []
leak_counter = 0


class LeakyObject:
    """
    Object class for memory leak demonstration.
    Each instance holds approximately 10KB of data.
    """
    def __init__(self, obj_id: int):
        self.id = obj_id
        self.payload = bytearray(2 * 1024)  # 2KB payload per object
        self.timestamp = time.time()
        self.description = f"LeakyObject_{obj_id}_{os.urandom(16).hex()}"

        # Fill payload with data
        fill = list(np.random.randint(0, 255, len(self.payload)))
        #list.sort(fill)

        for i in range(len(self.payload)):
            self.payload[i] = fill[i]


def main():
    """Main entry point."""
    print("=== ProfilingTarget Application (Python) ===")
    print("This application has intentional performance issues.")
    print("Use Scalene to identify them.\n")

    # Create temp directory for I/O operations
    temp_dir = Path(tempfile.mkdtemp(prefix="profiling_lab_"))
    print(f"Working directory: {temp_dir}")

    iterations = 50
    if len(sys.argv) > 1:
        try:
            iterations = int(sys.argv[1])
        except ValueError:
            print(f"Invalid iteration count, using default: {iterations}")

    print(f"Running {iterations} iterations...")

    for i in range(iterations):
        # CPU-intensive operations
        run_cpu_intensive_work()

        # Disk I/O operations - distributed across multiple methods
        run_disk_io_work(temp_dir, i)
        disk_io_hotspot(temp_dir)

        # Memory leak accumulation
        accumulate_memory_leak()

        # Simulate some native code time
        #native_computation()

        # Small delay to make profiling easier
        time.sleep(0.1)

    # Cleanup temp files
    cleanup_temp_dir(temp_dir)

    print("\n=== Application completed ===")
    print(f"Iterations completed: {iterations}")
    print(f"Leaked objects in cache: {len(leaky_cache)}")


def run_cpu_intensive_work():
    """CPU-intensive operations with multiple hotspots."""
    # CPU HOTSPOT #1: Find primes inefficiently
    limit = 2000  # Reduced from 10000 to balance with other hotspots
    primes = find_primes_inefficient(limit)

    # CPU HOTSPOT #2: Inefficient string building
    report = build_report_inefficient(primes)

    # CPU HOTSPOT #3: Unnecessary hash computation
    compute_hashes_inefficient(primes)

    # MEMORY ALLOCATION HOTSPOT: Creating many temporary lists
    process_data_with_allocations(primes)


def find_primes_inefficient(limit: int) -> List[int]:
    """
    CPU HOTSPOT: Trial division checking every number, no optimizations.
    
    Issues:
    - Checks all numbers up to num-1 instead of sqrt(num)
    - Checks even divisors for odd numbers
    - Doesn't break early when factor found
    - Uses list append in tight loop (minor allocation issue)
    """
    primes = []

    for num in range(2, limit + 1):
        is_prime = True
        # Inefficient: checks all numbers up to num-1
        for div in range(2, num):
            if num % div == 0:
                is_prime = False
                # Inefficient: doesn't break, continues checking all divisors

        if is_prime:
            primes.append(num)

    return primes


def build_report_inefficient(numbers: List[int]) -> str:
    """
    CPU HOTSPOT: String concatenation in a loop.
    Creates many temporary string objects.
    
    Issue: Using += for string building instead of join() or io.StringIO
    """
    result = ""  # Inefficient: should use list + join or StringIO

    # Increased iterations and added nested string operations
    for i, num in enumerate(numbers):
        # Each concatenation creates a new string object
        result = result + f"Number {i}: {num}\n"

        # Extra inefficiency: multiple unnecessary string operations per iteration
        temp = f"Processing item {i} with value {num} at index {i}"
        temp = temp + " - additional processing data"
        temp = temp.upper() + temp.lower()  # More string allocations

        # Even more string work
        for j in range(5):
            detail = f"  Detail {j}: num={num}, squared={num*num}, cubed={num*num*num}"
            result = result + detail + "\n"

    return result

def native_computation():
    """A dummy native computation to simulate native code time."""
    # Create two massive matrices
    size = 100
    matrix_a = np.random.rand(size, size)
    matrix_b = np.random.rand(size, size)
    result = np.zeros((size, size))

    # This operation happens almost entirely in native code
    for _ in range(1000):
        np.dot(matrix_a, matrix_b, out=result)

    return result

def compute_hashes_inefficient(numbers: List[int]) -> None:
    """
    CPU HOTSPOT: Computing hashes inefficiently.
    
    Issues:
    - Creating new hasher for each number
    - Converting bytes to hex character by character
    - Unnecessary string operations
    """
    for i, num in enumerate(numbers):  # Process all numbers, not just first 200
        # Multiple hash rounds per number
        for round_num in range(3):
            # Creating new hasher for each number (inefficient)
            hasher = hashlib.sha256()
            input_str = f"prime_{num}_round_{round_num}"

            # Hashing character by character (very inefficient)
            for char in input_str:
                hasher.update(char.encode('utf-8'))

            hash_bytes = hasher.digest()

            # Inefficient hex conversion
            hex_hash = ""
            for byte in hash_bytes:
                hex_hash = hex_hash + format(byte, '02x')

            # Additional inefficient operations
            reversed_hash = ""
            for char in hex_hash:
                reversed_hash = char + reversed_hash


def process_data_with_allocations(numbers: List[int]) -> None:
    """
    MEMORY ALLOCATION HOTSPOT: Creates many temporary objects.
    
    Issues:
    - Creating new lists in each iteration
    - Unnecessary copying of data
    - Creating temporary dictionaries
    """
    for i in range(50):
        # Create temporary list (allocation)
        temp_list = list(numbers)  # Copy all numbers, not just first 100

        # Create temporary dict (allocation)
        temp_dict = {j: temp_list[j % len(temp_list)] for j in range(len(temp_list))}

        # Create another copy (allocation)
        another_copy = temp_list.copy()

        # More allocations with list comprehension
        #doubled = [x * 2 for x in another_copy]
        #tripled = [x * 3 for x in another_copy]

        # String allocations - more of them
        #descriptions = [f"Value_{x}_iter_{i}" for x in doubled]
        #more_strings = [f"Data_{x}_{i}" for x in tripled]

        # Inefficient sorting operations
        sorted_copy = sorted(another_copy, reverse=True)
        sorted_again = sorted(sorted_copy)


def run_disk_io_work(temp_dir: Path, iteration: int) -> None:
    """Disk I/O operations distributed across multiple methods for interesting flame graphs."""
    # I/O HOTSPOT #1: Application logging simulation
    log_file = temp_dir / "application.log"
    write_application_log(log_file, iteration)

    # I/O HOTSPOT #2: Data export with inefficient I/O
    data_file = temp_dir / f"data_export_{iteration}.txt"
    export_data_inefficient(data_file, iteration)

    # I/O HOTSPOT #3: Configuration file operations
    config_file = temp_dir / "config.properties"
    process_config_file(config_file, iteration)

    # I/O HOTSPOT #4: Audit trail with byte-by-byte operations
    audit_file = temp_dir / "audit.log"
    write_audit_trail(audit_file, iteration)

    # Cleanup iteration-specific files
    if data_file.exists():
        data_file.unlink()


def disk_io_hotspot(temp_dir: Path):
    """
    Disk IO Hotspot: Excessive file operations
    """
    try:

        # Write many small files
        for i in range(10):
            filename = temp_dir / f"file_{time.time_ns()}_{i}.txt"
            with open(filename, 'w') as f:
                # Write small amount of data
                f.write(f"This is test data line {i}\n")
                f.flush()  # Force disk sync
                os.fsync(f.fileno())  # Ensure data is written to disk

        # Read all files in directory
        for file_path in temp_dir.glob("*.txt"):
            if file_path.is_file():
                with open(file_path, 'r') as f:
                    for line in f:
                        # Process line (minimal work)
                        len(line)

        # Delete old files (keep only recent ones)
        files = sorted(temp_dir.glob("*.txt"), key=lambda x: x.stat().st_mtime)
        if len(files) > 50:
            for file_path in files[:-50]:
                file_path.unlink()

    except Exception as e:
        print(f"IO Error: {e}")


def write_application_log(log_file: Path, iteration: int) -> None:
    """
    DISK I/O HOTSPOT: Simulates inefficient application logging.
    Writes log entries one character at a time with flush after each.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] INFO  Iteration {iteration} started - Processing data batch\n"

    # Append mode, character by character
    with open(log_file, 'a', buffering=1) as f:
        for char in log_entry:
            f.write(char)
            f.flush()

    # Add some "debug" log entries
    write_debug_log_entries(log_file, iteration)


def write_debug_log_entries(log_file: Path, iteration: int) -> None:
    """
    DISK I/O HOTSPOT: Additional logging method to create deeper call stack.
    """
    debug_messages = [
        "Cache status: checking validity",
        "Memory pool: allocating buffer",
        "Thread pool: task queued"
    ]

    with open(log_file, 'a', buffering=1) as f:
        for msg in debug_messages:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry = f"[{timestamp}] DEBUG {msg} (iter={iteration})\n"
            for char in entry:
                f.write(char)
            f.flush()


def export_data_inefficient(data_file: Path, iteration: int) -> None:
    """
    DISK I/O HOTSPOT: Simulates data export with inefficient file operations.
    """
    # Create data records
    records = generate_data_records(iteration)

    # Write records inefficiently
    with open(data_file, 'w', buffering=1) as f:
        for record in records:
            write_record_char_by_char(f, record)

    # Verify by reading back (also inefficient)
    verify_exported_data(data_file)


def generate_data_records(iteration: int) -> List[str]:
    """Helper: Generate sample data records."""
    records = []
    for i in range(20):
        record = f"RECORD|{iteration}|{i}|{uuid.uuid4().hex[:8]}|{hash(i) % 1000:.2f}\n"
        records.append(record)
    return records


def write_record_char_by_char(f, record: str) -> None:
    """
    DISK I/O HOTSPOT: Write a single record character by character.
    """
    for char in record:
        f.write(char)
    f.flush()


def verify_exported_data(data_file: Path) -> None:
    """
    DISK I/O HOTSPOT: Verify exported data by reading character by character.
    """
    content = ""
    with open(data_file, 'r', buffering=1) as f:
        while True:
            char = f.read(1)
            if not char:
                break
            content = content + char

    # Simulate checksum verification
    checksum = sum(ord(c) for c in content)


def process_config_file(config_file: Path, iteration: int) -> None:
    """
    DISK I/O HOTSPOT: Configuration file operations.
    """
    # Write config
    write_config_properties(config_file, iteration)

    # Read and parse config
    read_config_properties(config_file)


def write_config_properties(config_file: Path, iteration: int) -> None:
    """
    DISK I/O HOTSPOT: Write configuration properties inefficiently.
    """
    properties = [
        "app.name=ProfilingTarget",
        "app.version=1.0.0",
        f"app.iteration={iteration}",
        f"app.timestamp={int(time.time() * 1000)}",
        "cache.enabled=true",
        "cache.size=1024",
        "logging.level=DEBUG"
    ]

    with open(config_file, 'w', buffering=1) as f:
        for prop in properties:
            line = prop + "\n"
            for char in line:
                f.write(char)
            f.flush()


def read_config_properties(config_file: Path) -> Dict[str, str]:
    """
    DISK I/O HOTSPOT: Read configuration properties character by character.
    """
    config = {}
    content = ""

    with open(config_file, 'r', buffering=1) as f:
        while True:
            char = f.read(1)
            if not char:
                break
            content = content + char

    # Parse properties
    for line in content.split("\n"):
        if "=" in line:
            key, value = line.split("=", 1)
            config[key] = value

    return config


def write_audit_trail(audit_file: Path, iteration: int) -> None:
    """
    DISK I/O HOTSPOT: Write audit trail entries.
    """
    # Write main audit entry
    write_audit_entry(audit_file, "ITERATION_START", iteration, "main")

    # Write sub-operation audit entries
    write_operation_audit(audit_file, iteration)

    # Write completion entry
    write_audit_entry(audit_file, "ITERATION_END", iteration, "main")


def write_audit_entry(audit_file: Path, action: str, iteration: int, component: str) -> None:
    """
    DISK I/O HOTSPOT: Write a single audit entry.
    """
    timestamp = int(time.time() * 1000)
    entry = f"{timestamp}|{action}|{component}|MainThread|{iteration}\n"

    with open(audit_file, 'a', buffering=1) as f:
        for char in entry:
            f.write(char)
            f.flush()


def write_operation_audit(audit_file: Path, iteration: int) -> None:
    """
    DISK I/O HOTSPOT: Write operation-specific audit entries.
    """
    operations = ["CPU_WORK", "MEMORY_ALLOC", "DATA_PROCESS"]

    for op in operations:
        write_audit_entry(audit_file, op, iteration, "worker")


def accumulate_memory_leak() -> None:
    """
    MEMORY LEAK: Accumulates objects that are never released.
    
    Issue: Objects are added to global list and never removed,
    causing memory to grow indefinitely.
    """
    global leak_counter

    # Each iteration adds more objects to the global list
    for _ in range(100):
        leak_counter += 1
        # Creating objects that will never be garbage collected
        obj = LeakyObject(leak_counter)
        leaky_cache.append(obj)  # Objects accumulate and are never removed


def cleanup_temp_dir(temp_dir: Path) -> None:
    """Cleanup temporary directory."""
    try:
        shutil.rmtree(temp_dir)
        print("Cleaned up temp directory")
    except Exception as e:
        print(f"Failed to cleanup: {e}")


if __name__ == "__main__":
    main()
