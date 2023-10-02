import * as THREE from 'three';
import { OrbitControls } from 'OrbitControls';
import { OBJLoader } from 'OBJLoader';
import { MTLLoader } from 'MTLLoader';
import { RectAreaLightHelper } from 'RectAreaLightHelper'
import { RectAreaLightUniformsLib } from 'RectAreaLightUniformsLib';

const urlParams = new URLSearchParams(window.location.search);
const view3d_url = urlParams.get('3d_url');
const view3D = urlParams.get('view_3d');
function init() {
    let container = document.querySelector('.container');
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

            // Model
            {
                var modelURL = view3d_url
                const loader = new OBJLoader();
                loader.load(modelURL, obj => {
                    scene.add(obj);
                },
                function (xhr) {
                    console.log((xhr.loaded / xhr.total * 100) + '% loaded');
                },
                function (error) {
                    console.log('Error ->' + error)
                }
                )
            }

            {
                const light = new THREE.DirectionalLight(0xffffff, 1)
                light.position.set(-2, 0, 10)
                light.lookAt(0, -1, 0)
                scene.add(light)

                // Helper
                // const helper = new THREE.DirectionalLightHelper(light, 5)
                // scene.add(helper)
            }

    {
        const light = new THREE.DirectionalLight(0xffffff, 1)
        light.position.set(2, 0, 5)
        light.lookAt(0, 1, 0)
        scene.add(light)
    }

    // OrbitControls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.autoRotate = true;
    controls.autoRotateSpeed = 5;
    controls.enableDamping = true;

    // Resize
    window.addEventListener('resize', onWindowResize, false)

    function onWindowResize() {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();

        renderer.setSize(window.innerWidth, window.innerHeight)
    }

    // Animate
    function animate() {
        requestAnimationFrame(animate)
        controls.update();
        renderer.render(scene, camera)
    }
    animate()
}
if(view3D == 'true'){
init()
}
