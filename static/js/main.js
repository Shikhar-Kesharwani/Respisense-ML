document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const imagePreview = document.getElementById('image-preview');
    const dropZoneContent = document.getElementById('drop-zone-content');
    const btnPredict = document.getElementById('btn-predict');
    const btnUpload = document.getElementById('btn-upload');
    const loaderOverlay = document.getElementById('loader-overlay');
    const statusBadge = document.getElementById('status-badge');
    const resultEmpty = document.getElementById('result-empty');
    const resultContent = document.getElementById('result-content');
    const predictionValue = document.getElementById('prediction-value');
    const confidenceFill = document.getElementById('confidence-fill');
    
    // Grad-CAM Elements
    const heatmapContainer = document.getElementById('heatmap-container');
    const heatmapPreview = document.getElementById('heatmap-preview');
    
    // New 3D Elements
    const glassPanel = document.querySelector('.glass-panel');
    const scannerLaser = document.getElementById('scanner-laser');

    let currentBase64 = null;

    // --- 3D Glass Panel Tilt Effect ---
    document.addEventListener('mousemove', (e) => {
        if (!glassPanel) return;
        // Calculate tilt based on mouse position relative to screen center
        const xAxis = (window.innerWidth / 2 - e.pageX) / 60;
        const yAxis = (window.innerHeight / 2 - e.pageY) / 60;
        
        // Apply the 3D rotation along with the existing glowing box-shadow
        glassPanel.style.transform = `perspective(1200px) rotateY(${xAxis}deg) rotateX(${yAxis}deg) translateZ(10px)`;
    });

    // Reset tilt when mouse leaves the window
    document.addEventListener('mouseleave', () => {
        if (!glassPanel) return;
        glassPanel.style.transform = `perspective(1200px) rotateY(0deg) rotateX(0deg) translateZ(0px)`;
    });

    // Trigger file input on click
    btnUpload.addEventListener('click', () => {
        fileInput.click();
    });

    dropZone.addEventListener('click', (e) => {
        if(e.target !== btnUpload) {
            fileInput.click();
        }
    });

    // Drag and Drop Events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('dragover');
        }, false);
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    });

    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        if (files.length === 0) return;
        
        const file = files[0];
        if (!file.type.match('image.*')) {
            alert('Please upload an image file (JPEG/PNG)');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            // Display Image Preview
            imagePreview.src = e.target.result;
            imagePreview.style.display = 'block';
            dropZoneContent.style.opacity = '0';
            
            // Extract Base64 without header
            currentBase64 = e.target.result.replace(/^data:image.+;base64,/, '');
            
            // Enable Predict Button
            btnPredict.disabled = false;
            statusBadge.textContent = 'Ready to Analyze';
            statusBadge.className = 'status-badge ready';
            
            // Reset Results & Scanner
            resultContent.style.display = 'none';
            resultEmpty.style.display = 'flex';
            confidenceFill.style.width = '0%';
            if(heatmapContainer) heatmapContainer.style.display = 'none';
            if(scannerLaser) scannerLaser.style.display = 'none';
        };
        reader.readAsDataURL(file);
    }

    // Prediction Logic
    btnPredict.addEventListener('click', async () => {
        if (!currentBase64) return;

        // Show Loader & 3D Scanner overlay
        loaderOverlay.classList.add('active');
        if(scannerLaser) scannerLaser.style.display = 'block';
        btnPredict.disabled = true;

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ image: currentBase64 })
            });

            const data = await response.json();
            
            let predictionStr = "";
            let heatmapBase64 = "";
            if (Array.isArray(data) && data.length > 0 && data[0].image) {
                predictionStr = data[0].image;
                heatmapBase64 = data[0].heatmap || "";
            } else {
                predictionStr = "Error parsing result";
            }

            displayResult(predictionStr, heatmapBase64);

        } catch (error) {
            console.error('Error during prediction:', error);
            alert('An error occurred while analyzing the scan. Ensure the server is running.');
            displayResult("Error");
        } finally {
            loaderOverlay.classList.remove('active');
            if(scannerLaser) scannerLaser.style.display = 'none';
            btnPredict.disabled = false;
        }
    });

    function displayResult(prediction, heatmap) {
        resultEmpty.style.display = 'none';
        resultContent.style.display = 'block';
        
        predictionValue.textContent = prediction;
        predictionValue.classList.remove('cancer', 'normal');
        
        // Add specific coloring and dummy confidence for UI flair
        setTimeout(() => {
            if (prediction.toLowerCase().includes('normal')) {
                predictionValue.classList.add('normal');
                confidenceFill.style.width = '99%';
            } else if (prediction.toLowerCase().includes('cancer') || prediction.toLowerCase().includes('adenocarcinoma')) {
                predictionValue.classList.add('cancer');
                confidenceFill.style.width = '98%';
            } else {
                confidenceFill.style.width = '0%';
            }
        }, 100);
        
        // Render Heatmap if it exists
        if (heatmap && heatmapContainer && heatmapPreview) {
            heatmapPreview.src = 'data:image/jpeg;base64,' + heatmap;
            heatmapContainer.style.display = 'block';
        }
        
        statusBadge.textContent = 'Analysis Complete';
    }
});

// --- NEW: Three.js 3D Interactive Background ---
const canvas = document.getElementById('three-canvas');
if (canvas && typeof THREE !== 'undefined') {
    const scene = new THREE.Scene();
    
    // Transparent background so our CSS gradient shows through
    const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);

    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 50;

    // Create a 3D particle system (medical nodes)
    const particlesGeometry = new THREE.BufferGeometry();
    const particlesCount = 1500;
    
    const posArray = new Float32Array(particlesCount * 3);
    for(let i = 0; i < particlesCount * 3; i++) {
        // Spread particles over a large 3D area
        posArray[i] = (Math.random() - 0.5) * 200;
    }
    
    particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
    
    // Create soft glowing cyan material
    const material = new THREE.PointsMaterial({
        size: 0.8,
        color: 0x00f2fe,
        transparent: true,
        opacity: 0.8,
        blending: THREE.AdditiveBlending
    });
    
    const particlesMesh = new THREE.Points(particlesGeometry, material);
    scene.add(particlesMesh);

    // Add some larger blurred "data nodes" floating around
    const bigGeometry = new THREE.BufferGeometry();
    const bigPosArray = new Float32Array(100 * 3);
    for(let i = 0; i < 100 * 3; i++) {
        bigPosArray[i] = (Math.random() - 0.5) * 150;
    }
    bigGeometry.setAttribute('position', new THREE.BufferAttribute(bigPosArray, 3));
    const bigMaterial = new THREE.PointsMaterial({
        size: 3,
        color: 0x0077b6,
        transparent: true,
        opacity: 0.5,
        blending: THREE.AdditiveBlending
    });
    const bigParticlesMesh = new THREE.Points(bigGeometry, bigMaterial);
    scene.add(bigParticlesMesh);

    // Mouse interactivity variables
    let mouseX = 0;
    let mouseY = 0;

    document.addEventListener('mousemove', (event) => {
        mouseX = (event.clientX / window.innerWidth) - 0.5;
        mouseY = (event.clientY / window.innerHeight) - 0.5;
    });

    const clock = new THREE.Clock();

    function animate() {
        requestAnimationFrame(animate);
        const elapsedTime = clock.getElapsedTime();

        // Slow constant rotation
        particlesMesh.rotation.y = elapsedTime * 0.05;
        particlesMesh.rotation.x = elapsedTime * 0.02;
        
        bigParticlesMesh.rotation.y = elapsedTime * 0.03;
        bigParticlesMesh.rotation.z = elapsedTime * 0.02;

        // Dynamic camera panning based on mouse movement (Parallax)
        camera.position.x += (mouseX * 20 - camera.position.x) * 0.05;
        camera.position.y += (-mouseY * 20 - camera.position.y) * 0.05;
        camera.lookAt(scene.position);

        renderer.render(scene, camera);
    }

    animate();

    // Handle window resize
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
}
