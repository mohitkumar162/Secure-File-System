const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ alpha: true });
renderer.setSize(window.innerWidth, window.innerHeight);
const backgroundDiv = document.getElementById('background');
backgroundDiv.appendChild(renderer.domElement);

// Add subtle ambient light
const ambientLight = new THREE.AmbientLight(0x404040);
scene.add(ambientLight);

camera.position.z = 200;

// Define sphere as an empty invisible 3D object to resolve the JS ReferenceError in the animation loop
const sphere = new THREE.Object3D();
scene.add(sphere);

// Add Floating Objects
const icons = ['🛡️', '🔒', '🔑', '✅', '🌐', '💾']; // Simple emoji representations
const floatingContainer = document.createElement('div');
floatingContainer.className = 'floating-objects';
backgroundDiv.appendChild(floatingContainer);

icons.forEach((icon, index) => {
    const obj = document.createElement('div');
    obj.className = `floating-object floating-${index + 1}`;
    obj.textContent = icon;
    obj.style.fontSize = '48px';
    obj.style.color = 'rgba(0, 255, 204, 0.3)';
    obj.style.textShadow = '0 0 15px rgba(59, 130, 246, 0.5)';
    floatingContainer.appendChild(obj);
});

function animate() {
    requestAnimationFrame(animate);
    sphere.rotation.x += 0.002;
    sphere.rotation.y += 0.003;
    renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', () => {
    renderer.setSize(window.innerWidth, window.innerHeight);
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
});