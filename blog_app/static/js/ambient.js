/**
 * Ambient Reactive Visual Engine
 * Lightweight, 60fps vanilla JS canvas integration.
 * Creates an interactive neural mesh mimicking high-end SaaS designs.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Accessibility check: Do not execute heavy animation if user requests reduced motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (prefersReducedMotion.matches) return;

    // Dynamically inject canvas element perfectly behind existing UI hierarchy
    const canvas = document.createElement('canvas');
    canvas.id = 'ambient-canvas';
    // Style directly for implicit integration (no CSS changes needed)
    Object.assign(canvas.style, {
        position: 'fixed',
        top: '0',
        left: '0',
        width: '100vw',
        height: '100vh',
        zIndex: '-998', // Placed just above the blurred CSS blobs, but behind all DOM cards
        pointerEvents: 'none', // Crucial: lets clicks pass through to the blog UI safely
        opacity: '0.8',
        transition: 'opacity 2s ease-in'
    });
    
    document.body.prepend(canvas);
    const ctx = canvas.getContext('2d');
    let width, height;
    
    // Engine Config - Automatically scales density based on device width to preserve FPS
    const isMobile = window.innerWidth < 768;
    const particleCount = isMobile ? 30 : 70;
    const connectionRadius = isMobile ? 12000 : 25000;
    
    const particles = [];
    const mouse = { x: null, y: null, radius: 180 };

    // Handle Resize & DPI Scaling (Debounced for performance)
    let resizeTimeout;
    function resize() {
        if (resizeTimeout) cancelAnimationFrame(resizeTimeout);
        resizeTimeout = requestAnimationFrame(() => {
            const dpr = window.devicePixelRatio || 1;
            width = window.innerWidth;
            height = window.innerHeight;
            
            canvas.width = width * dpr;
            canvas.height = height * dpr;
            ctx.scale(dpr, dpr);
        });
    }
    window.addEventListener('resize', resize, { passive: true });
    resize();

    // Subtle Parallax & Interaction Listeners
    window.addEventListener('mousemove', (e) => {
        mouse.x = e.x;
        mouse.y = e.y;
    }, { passive: true });
    
    // Gently fade interaction when leaving viewport
    window.addEventListener('mouseout', () => {
        mouse.x = null;
        mouse.y = null;
    });

    // Particle Object mapped to Django's primary/accent CSS
    class AmbientNode {
        constructor() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.size = Math.random() * 2 + 0.5;
            this.baseX = this.x;
            this.baseY = this.y;
            this.density = (Math.random() * 20) + 5;
            
            // Randomize between Indigo (--primary) and Soft Cyan
            this.color = Math.random() > 0.5 ? 'rgba(99, 102, 241, 0.6)' : 'rgba(6, 182, 212, 0.4)';
            
            // Ultra-slow continuous ambient drift
            this.vx = (Math.random() - 0.5) * 0.4;
            this.vy = (Math.random() - 0.5) * 0.4;
        }

        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = this.color;
            ctx.fill();
        }

        update() {
            // Ambient roaming
            this.x += this.vx;
            this.y += this.vy;

            // Soft boundary wrap around
            if (this.x < 0) this.x = width;
            if (this.x > width) this.x = 0;
            if (this.y < 0) this.y = height;
            if (this.y > height) this.y = 0;

            // Elegant repelling mouse interaction
            if (mouse.x != null) {
                let dx = mouse.x - this.x;
                let dy = mouse.y - this.y;
                let distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < mouse.radius) {
                    let forceDirectionX = dx / distance;
                    let forceDirectionY = dy / distance;
                    let maxDistance = mouse.radius;
                    // Exponential backoff for softer push
                    let force = (maxDistance - distance) / maxDistance;
                    
                    let directionX = forceDirectionX * force * this.density;
                    let directionY = forceDirectionY * force * this.density;
                    
                    this.x -= directionX * 0.2;
                    this.y -= directionY * 0.2;
                }
            }
        }
    }

    // Initialize Network
    for (let i = 0; i < particleCount; i++) {
        particles.push(new AmbientNode());
    }

    // Main Engine Loop
    function animate() {
        ctx.clearRect(0, 0, width, height);
        
        for (let i = 0; i < particles.length; i++) {
            particles[i].update();
            particles[i].draw();

            // Connect nearby nodes to form neural mesh
            for (let j = i; j < particles.length; j++) {
                let dx = particles[i].x - particles[j].x;
                let dy = particles[i].y - particles[j].y;
                let distanceSq = dx * dx + dy * dy;
                
                if (distanceSq < connectionRadius) {
                    // Calculate opacity based on distance
                    let opacity = 1 - (distanceSq / connectionRadius);
                    
                    ctx.beginPath();
                    ctx.strokeStyle = `rgba(99, 102, 241, ${opacity * 0.25})`; // Soft Indigo link
                    ctx.lineWidth = 0.6;
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }
        }
        requestAnimationFrame(animate);
    }
    
    // Start Engine
    animate();
});
