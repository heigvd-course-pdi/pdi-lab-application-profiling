import java.io.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import java.util.concurrent.*;

/**
 * ProfilingTarget - A Java application with intentional performance issues
 * for students to discover using async-profiler and JFR/JMC.
 * 
 * Issues to find:
 * 1. CPU Hotspot: Inefficient prime number calculation
 * 2. CPU Hotspot: Unnecessary string concatenation in loop
 * 3. Memory Leak: Objects retained in a static list that grows indefinitely
 * 4. Disk I/O Hotspot: Synchronous file writes without buffering
 * 5. Disk I/O Hotspot: Reading files byte-by-byte
 */
public class ProfilingTarget {
    
    // MEMORY LEAK: Static list that accumulates objects and is never cleared
    private static final List<LeakyObject> leakyCache = new ArrayList<>();
    
    // Counter for leak demonstration
    private static int leakCounter = 0;
    
    public static void main(String[] args) throws Exception {
        System.out.println("=== ProfilingTarget Application ===");
        System.out.println("This application has intentional performance issues.");
        System.out.println("Use async-profiler or JFR/JMC to identify them.\n");
        
        // Create temp directory for I/O operations
        Path tempDir = Files.createTempDirectory("profiling_lab");
        System.out.println("Working directory: " + tempDir);
        
        int iterations = 1000;
        if (args.length > 0) {
            try {
                iterations = Integer.parseInt(args[0]);
            } catch (NumberFormatException e) {
                System.out.println("Invalid iteration count, using default: " + iterations);
            }
        }
        
        System.out.println("Running " + iterations + " iterations...");
        
        for (int i = 0; i < iterations; i++) {
            // CPU-intensive operations
            runCpuIntensiveWork();
            
            // Disk I/O operations - distributed across multiple methods
            runDiskIoWork(tempDir, i);
            
            // Memory leak accumulation
            accumulateMemoryLeak();
            
            // Small delay to make profiling easier
            Thread.sleep(100);
        }
        
        // Cleanup temp files
        cleanupTempDir(tempDir);
        
        System.out.println("\n=== Application completed ===");
        System.out.println("Iterations completed: " + iterations);
        System.out.println("Leaked objects in cache: " + leakyCache.size());
        System.out.println("Approximate leaked memory: " + (leakyCache.size() * 10240) + " bytes");
    }
    
    /**
     * CPU HOTSPOT #1: Extremely inefficient prime number calculation
     * Uses trial division without any optimizations
     */
    private static void runCpuIntensiveWork() {
        // Find primes up to this number (inefficiently)
        int limit = 10000;
        List<Integer> primes = findPrimesInefficient(limit);
        
        // CPU HOTSPOT #2: Inefficient string building
        String report = buildReportInefficient(primes);
        
        // CPU HOTSPOT #3: Unnecessary hash computation
        computeHashesInefficient(primes);
    }
    
    /**
     * CPU HOTSPOT: Trial division checking every number, no optimizations
     */
    private static List<Integer> findPrimesInefficient(int limit) {
        List<Integer> primes = new ArrayList<>();
        
        for (int num = 2; num <= limit; num++) {
            boolean isPrime = true;
            // Inefficient: checks all numbers up to num-1 instead of sqrt(num)
            // Also checks even divisors even for odd numbers
            for (int div = 2; div < num; div++) {
                if (num % div == 0) {
                    isPrime = false;
                    // Inefficient: doesn't break early, continues checking
                }
            }
            if (isPrime) {
                primes.add(num);
            }
        }
        return primes;
    }
    
    /**
     * CPU HOTSPOT: String concatenation in a loop
     * Creates many temporary String objects
     */
    private static String buildReportInefficient(List<Integer> numbers) {
        String result = "";  // Inefficient: should use StringBuilder
        
        for (int i = 0; i < Math.min(numbers.size(), 500); i++) {
            // Each concatenation creates a new String object
            result = result + "Number " + i + ": " + numbers.get(i) + "\n";
        }
        
        return result;
    }
    
    /**
     * CPU HOTSPOT: Computing hashes inefficiently
     */
    private static void computeHashesInefficient(List<Integer> numbers) {
        try {
            for (int i = 0; i < Math.min(numbers.size(), 200); i++) {
                // Creating new MessageDigest instance for each number (inefficient)
                MessageDigest md = MessageDigest.getInstance("SHA-256");
                String input = "prime_" + numbers.get(i);
                
                // Converting to bytes and hashing character by character
                for (char c : input.toCharArray()) {
                    md.update((byte) c);
                }
                byte[] hash = md.digest();
                
                // Inefficient hex conversion
                String hexHash = "";
                for (byte b : hash) {
                    hexHash = hexHash + String.format("%02x", b);
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    /**
     * DISK I/O HOTSPOTS - Distributed across multiple methods for interesting flame graphs
     */
    private static void runDiskIoWork(Path tempDir, int iteration) throws IOException {
        // I/O HOTSPOT #1: Unbuffered writes via logging simulation
        Path logFile = tempDir.resolve("application.log");
        writeApplicationLog(logFile, iteration);
        
        // I/O HOTSPOT #2: Data export with inefficient I/O
        Path dataFile = tempDir.resolve("data_export_" + iteration + ".txt");
        exportDataInefficient(dataFile, iteration);
        
        // I/O HOTSPOT #3: Configuration file operations
        Path configFile = tempDir.resolve("config.properties");
        processConfigFile(configFile, iteration);
        
        // I/O HOTSPOT #4: Audit trail with byte-by-byte operations
        Path auditFile = tempDir.resolve("audit.log");
        writeAuditTrail(auditFile, iteration);
        
        // Cleanup iteration-specific files
        Files.deleteIfExists(dataFile);
    }
    
    /**
     * DISK I/O HOTSPOT: Simulates inefficient application logging
     * Writes log entries one character at a time with flush after each
     */
    private static void writeApplicationLog(Path logFile, int iteration) throws IOException {
        String logEntry = String.format("[%tF %<tT] INFO  Iteration %d started - Processing data batch%n", 
                                        new Date(), iteration);
        
        // Append mode, unbuffered
        try (FileOutputStream fos = new FileOutputStream(logFile.toFile(), true)) {
            // Writing one byte at a time (very inefficient for logging)
            for (byte b : logEntry.getBytes()) {
                fos.write(b);
                fos.flush();  // Flushing after every byte
            }
        }
        
        // Add some "debug" log entries
        writeDebugLogEntries(logFile, iteration);
    }
    
    /**
     * DISK I/O HOTSPOT: Additional logging method to create deeper call stack
     */
    private static void writeDebugLogEntries(Path logFile, int iteration) throws IOException {
        String[] debugMessages = {
            "Cache status: checking validity",
            "Memory pool: allocating buffer",
            "Thread pool: task queued"
        };
        
        try (FileOutputStream fos = new FileOutputStream(logFile.toFile(), true)) {
            for (String msg : debugMessages) {
                String entry = String.format("[%tF %<tT] DEBUG %s (iter=%d)%n", 
                                            new Date(), msg, iteration);
                for (byte b : entry.getBytes()) {
                    fos.write(b);
                }
                fos.flush();
            }
        }
    }
    
    /**
     * DISK I/O HOTSPOT: Simulates data export with inefficient file operations
     */
    private static void exportDataInefficient(Path dataFile, int iteration) throws IOException {
        // Create data records
        List<String> records = generateDataRecords(iteration);
        
        // Write records inefficiently
        try (FileOutputStream fos = new FileOutputStream(dataFile.toFile())) {
            for (String record : records) {
                writeRecordByteByByte(fos, record);
            }
        }
        
        // Verify by reading back (also inefficient)
        verifyExportedData(dataFile);
    }
    
    /**
     * Helper: Generate sample data records
     */
    private static List<String> generateDataRecords(int iteration) {
        List<String> records = new ArrayList<>();
        for (int i = 0; i < 20; i++) {
            records.add(String.format("RECORD|%d|%d|%s|%.2f%n", 
                        iteration, i, UUID.randomUUID().toString().substring(0, 8), 
                        Math.random() * 1000));
        }
        return records;
    }
    
    /**
     * DISK I/O HOTSPOT: Write a single record byte by byte
     */
    private static void writeRecordByteByByte(FileOutputStream fos, String record) throws IOException {
        for (byte b : record.getBytes()) {
            fos.write(b);
        }
        fos.flush();
    }
    
    /**
     * DISK I/O HOTSPOT: Verify exported data by reading byte by byte
     */
    private static void verifyExportedData(Path dataFile) throws IOException {
        StringBuilder content = new StringBuilder();
        try (FileInputStream fis = new FileInputStream(dataFile.toFile())) {
            int byteRead;
            while ((byteRead = fis.read()) != -1) {
                content.append((char) byteRead);
            }
        }
        // Simulate checksum verification
        int checksum = 0;
        for (char c : content.toString().toCharArray()) {
            checksum += c;
        }
    }
    
    /**
     * DISK I/O HOTSPOT: Configuration file operations
     */
    private static void processConfigFile(Path configFile, int iteration) throws IOException {
        // Write config
        writeConfigProperties(configFile, iteration);
        
        // Read and parse config
        readConfigProperties(configFile);
    }
    
    /**
     * DISK I/O HOTSPOT: Write configuration properties inefficiently
     */
    private static void writeConfigProperties(Path configFile, int iteration) throws IOException {
        String[] properties = {
            "app.name=ProfilingTarget",
            "app.version=1.0.0",
            "app.iteration=" + iteration,
            "app.timestamp=" + System.currentTimeMillis(),
            "cache.enabled=true",
            "cache.size=1024",
            "logging.level=DEBUG"
        };
        
        try (FileOutputStream fos = new FileOutputStream(configFile.toFile())) {
            for (String prop : properties) {
                String line = prop + "\n";
                for (byte b : line.getBytes()) {
                    fos.write(b);
                }
                fos.flush();
            }
        }
    }
    
    /**
     * DISK I/O HOTSPOT: Read configuration properties byte by byte
     */
    private static Map<String, String> readConfigProperties(Path configFile) throws IOException {
        Map<String, String> config = new HashMap<>();
        StringBuilder content = new StringBuilder();
        
        try (FileInputStream fis = new FileInputStream(configFile.toFile())) {
            int byteRead;
            while ((byteRead = fis.read()) != -1) {
                content.append((char) byteRead);
            }
        }
        
        // Parse properties
        for (String line : content.toString().split("\n")) {
            if (line.contains("=")) {
                String[] parts = line.split("=", 2);
                config.put(parts[0], parts[1]);
            }
        }
        
        return config;
    }
    
    /**
     * DISK I/O HOTSPOT: Write audit trail entries
     */
    private static void writeAuditTrail(Path auditFile, int iteration) throws IOException {
        // Write main audit entry
        writeAuditEntry(auditFile, "ITERATION_START", iteration, "main");
        
        // Write sub-operation audit entries
        writeOperationAudit(auditFile, iteration);
        
        // Write completion entry
        writeAuditEntry(auditFile, "ITERATION_END", iteration, "main");
    }
    
    /**
     * DISK I/O HOTSPOT: Write a single audit entry
     */
    private static void writeAuditEntry(Path auditFile, String action, int iteration, String component) 
            throws IOException {
        String entry = String.format("%d|%s|%s|%s|%d%n", 
                                    System.currentTimeMillis(), action, component, 
                                    Thread.currentThread().getName(), iteration);
        
        try (FileOutputStream fos = new FileOutputStream(auditFile.toFile(), true)) {
            for (byte b : entry.getBytes()) {
                fos.write(b);
                fos.flush();
            }
        }
    }
    
    /**
     * DISK I/O HOTSPOT: Write operation-specific audit entries
     */
    private static void writeOperationAudit(Path auditFile, int iteration) throws IOException {
        String[] operations = {"CPU_WORK", "MEMORY_ALLOC", "DATA_PROCESS"};
        
        for (String op : operations) {
            writeAuditEntry(auditFile, op, iteration, "worker");
        }
    }
    
    /**
     * MEMORY LEAK: Accumulates objects that are never released
     */
    private static void accumulateMemoryLeak() {
        // Each iteration adds more objects to the static list
        for (int i = 0; i < 100; i++) {
            leakCounter++;
            // Creating objects that will never be garbage collected
            LeakyObject obj = new LeakyObject(leakCounter);
            leakyCache.add(obj);  // Objects accumulate here and are never removed
        }
    }
    
    /**
     * Object class for memory leak demonstration
     * Each instance holds 10KB of data
     */
    static class LeakyObject {
        private final int id;
        private final byte[] payload;  // 10KB payload per object
        private final long timestamp;
        private final String description;
        
        public LeakyObject(int id) {
            this.id = id;
            this.payload = new byte[10 * 1024];  // 10KB
            this.timestamp = System.currentTimeMillis();
            this.description = "LeakyObject_" + id + "_" + UUID.randomUUID();
            
            // Fill payload with data
            Arrays.fill(payload, (byte) (id % 256));
        }
        
        public int getId() { return id; }
        public byte[] getPayload() { return payload; }
        public long getTimestamp() { return timestamp; }
        public String getDescription() { return description; }
    }
    
    /**
     * Cleanup temporary directory
     */
    private static void cleanupTempDir(Path tempDir) {
        try {
            Files.walk(tempDir)
                .sorted(Comparator.reverseOrder())
                .map(Path::toFile)
                .forEach(File::delete);
            System.out.println("Cleaned up temp directory");
        } catch (IOException e) {
            System.err.println("Failed to cleanup: " + e.getMessage());
        }
    }
}
