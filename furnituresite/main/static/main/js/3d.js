import * as THREE from 'three';
import { OrbitControls } from 'OrbitControls';
import { OBJLoader } from 'OBJLoader';
import { MTLLoader } from 'MTLLoader';
import { RectAreaLightHelper } from 'RectAreaLightHelper';
import { RectAreaLightUniformsLib } from 'RectAreaLightUniformsLib';

const urlParams = new URLSearchParams(window.location.search);
const view3d_url = urlParams.get('3d_url');
const view3D = urlParams.get('view_3d');
let isRotating = false;
let container = document.querySelector('.container');

function init() {
    // Scene
    const scene = new THREE.Scene()
    scene.background = new THREE.Color("#E2DFE1");

    // Camera
    const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 3000);
    camera.position.set(0, 0.5, 1.5);
    camera.lookAt(0, 0, 0);

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true })
    renderer.setSize(window.innerWidth, window.innerHeight)
    container.appendChild(renderer.domElement)

    let plain;
    {
        plain = new THREE.Mesh(
            new THREE.PlaneGeometry(1000, 1000),
            new THREE.MeshBasicMaterial({ color: "#E2DFE1" })
        )
        plain.receiveShadow = true;
        plain.position.set(0, -1, 0)
        plain.rotateX(-Math.PI / 2);
        scene.add(plain)
    }

    // Load your object using OBJLoader (assuming it's an OBJ file)
    let currentRotatingObject;

    function loadAndAddObject(url) {
        const loader = new OBJLoader();
        loader.load(url, obj => {
            // Remove previous rotating object if it exists
            if (currentRotatingObject) {
                scene.remove(currentRotatingObject);
            }
            currentRotatingObject = obj;
            scene.add(obj);
        },
        function (xhr) {
            console.log((xhr.loaded / xhr.total * 100) + '% loaded');
        },
        function (error) {
            console.log('Error ->' + error)
        });
    }

    // Model
    loadAndAddObject(view3d_url);

    // Lights
    const light1 = new THREE.DirectionalLight(0xffffff, 1)
    light1.position.set(-2, 0, 10)
    light1.lookAt(0, -1, 0)
    scene.add(light1)

    const light2 = new THREE.DirectionalLight(0xffffff, 1)
    light2.position.set(2, 0, 5)
    light2.lookAt(0, 1, 0)
    scene.add(light2)

    // OrbitControls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.autoRotate = false;
    controls.autoRotateSpeed = 5;
    controls.enableDamping = true;

    // Resize
    window.addEventListener('resize', onWindowResize, false)

    function onWindowResize() {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();

        renderer.setSize(window.innerWidth, window.innerHeight)
    }

    // Keyboard controls for object rotation and camera movement
    document.addEventListener('keydown', (event) => {
        switch (event.key) {
            case 'a': // Toggle auto-rotation on 'A' key
            case 'ф': // Toggle auto-rotation on 'A' key (Cyrillic)
                isRotating = !isRotating;
                break;
            case 'ArrowUp': // Move camera forward
                camera.position.y += 0.1;
                break;
            case 'ArrowDown': // Move camera backward
                camera.position.y -= 0.1;
                break;
            case 'ArrowLeft': // Move camera left
                camera.position.x -= 0.1;
                break;
            case 'ArrowRight': // Move camera right
                camera.position.x += 0.1;
                break;
        }
    });

    // Animate
    function animate() {
        requestAnimationFrame(animate)
        controls.update();
        if (isRotating && currentRotatingObject) {
            currentRotatingObject.rotation.y += 0.01;
        }
        renderer.render(scene, camera)
    }
    animate();
}

if (view3D == 'true') {
    init();
}
