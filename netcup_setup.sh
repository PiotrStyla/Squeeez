#!/bin/bash
# PAQ8px Setup Script for Netcup VPS
# Run: bash netcup_setup.sh

set -e  # Exit on error

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🚀 PAQ8px Environment Setup - Netcup VPS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Update system
echo "[1/8] Updating system packages..."
apt update && apt upgrade -y

# Install dependencies
echo "[2/8] Installing build tools and dependencies..."
apt install -y build-essential g++ gcc make wget git curl htop screen vim zip unzip

# Create working directory
echo "[3/8] Creating work directories..."
mkdir -p /root/hutter/data
cd /root/hutter

# Clone PAQ8px
echo "[4/8] Cloning PAQ8px repository..."
if [ -d "paq8px" ]; then
    echo "PAQ8px already exists, pulling latest..."
    cd paq8px && git pull && cd ..
else
    git clone https://github.com/hxim/paq8px.git
fi

cd paq8px

# Compile PAQ8px
echo "[5/8] Compiling PAQ8px (this may take a few minutes)..."
if [ -f "Makefile" ]; then
    make clean || true
    make -j$(nproc)
else
    # Fallback if no Makefile
    g++ -o paq8px *.cpp -O3 -march=native -std=c++17 -pthread
fi

# Verify compilation
echo "[6/8] Verifying PAQ8px compilation..."
if [ -f "paq8px" ]; then
    echo "✅ PAQ8px compiled successfully!"
    ./paq8px || echo "Binary check complete"
else
    echo "❌ Compilation failed!"
    exit 1
fi

# Setup model directory
echo "[7/8] Setting up model directory..."
mkdir -p build
cd build
pwd

# Create monitoring script
echo "[8/8] Creating monitoring script..."
cat > /root/hutter/monitor.sh << 'MONITOR'
#!/bin/bash
# Compression monitoring script

while true; do
    clear
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  📊 PAQ8px Compression Monitor"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    date
    echo ""
    
    # Process check
    if pgrep -f "paq8px" > /dev/null; then
        echo "Status: ✅ RUNNING"
        echo ""
        echo "Process info:"
        ps aux | grep paq8px | grep -v grep | head -1
        echo ""
    else
        echo "Status: ❌ NOT RUNNING"
        echo ""
    fi
    
    # Memory
    echo "Memory usage:"
    free -h | grep Mem
    echo ""
    
    # Output file
    echo "Output files:"
    ls -lh /root/hutter/paq8px/*.paq8 2>/dev/null | tail -5 || echo "No .paq8 files yet"
    echo ""
    
    # Disk
    echo "Disk space:"
    df -h / | grep -v Filesystem
    echo ""
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Refreshing in 60 seconds... (Ctrl+C to exit)"
    sleep 60
done
MONITOR

chmod +x /root/hutter/monitor.sh

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "  1. Upload data files:"
echo "     - enwik9_reordered_transformed → /root/hutter/paq8px/"
echo "     - english.rnn → /root/hutter/paq8px/build/"
echo "     - x86_64.rnn → /root/hutter/paq8px/build/"
echo ""
echo "  2. Start compression in screen:"
echo "     cd /root/hutter/paq8px"
echo "     screen -S compression"
echo "     ./paq8px -5r enwik9_reordered_transformed output.paq8"
echo ""
echo "  3. Monitor (optional):"
echo "     /root/hutter/monitor.sh"
echo ""
echo "PAQ8px location: /root/hutter/paq8px/paq8px"
echo "Monitor script: /root/hutter/monitor.sh"
echo ""
