#!/bin/bash
# SSL Certificate Setup Script for Sport Lottery Sweeper
# 体育彩票系统SSL证书配置脚本

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
DOMAIN="sport-lottery.example.com"
EMAIL="admin@sport-lottery.example.com"
WEBROOT="/var/www/certbot"
NGINX_CONTAINER="sport-lottery-nginx-prod"
CERTBOT_CONTAINER="certbot"

print_status() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

print_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ✗ $1${NC}"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_warning "Running as root is not recommended. Use sudo instead."
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p $WEBROOT
    mkdir -p nginx/ssl
    mkdir -p scripts/ssl-certificates
    
    print_success "Directories created"
}

# Generate self-signed certificate (for testing)
generate_self_signed_cert() {
    print_status "Generating self-signed SSL certificate for testing..."
    
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/sport-lottery.example.com.key \
        -out nginx/ssl/sport-lottery.example.com.crt \
        -subj "/C=CN/ST=Beijing/L=Beijing/O=Sport Lottery Sweeper/CN=$DOMAIN"
    
    print_success "Self-signed certificate generated"
    print_warning "Remember to replace with real certificates before production!"
}

# Setup Let's Encrypt certificate using Certbot
setup_letsencrypt() {
    print_status "Setting up Let's Encrypt certificate..."
    
    # Check if Docker is available
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    # Create certbot container for initial certificate
    docker run -it --rm --name $CERTBOT_CONTAINER \
        -v "$(pwd)/nginx/ssl:/etc/letsencrypt" \
        -v "$(pwd)/$WEBROOT:/var/www/certbot" \
        certbot/certbot certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        --email $EMAIL \
        --agree-tos \
        --no-eff-email \
        -d $DOMAIN -d www.$DOMAIN
    
    if [ $? -eq 0 ]; then
        print_success "Let's Encrypt certificate obtained successfully"
        
        # Copy certificates to nginx directory
        cp nginx/ssl/live/$DOMAIN/fullchain.pem nginx/ssl/sport-lottery.example.com.crt
        cp nginx/ssl/live/$DOMAIN/privkey.pem nginx/ssl/sport-lottery.example.com.key
        
        print_success "Certificates copied to nginx directory"
    else
        print_error "Failed to obtain Let's Encrypt certificate"
        print_warning "Falling back to self-signed certificate"
        generate_self_signed_cert
    fi
}

# Setup auto-renewal for Let's Encrypt
setup_auto_renewal() {
    print_status "Setting up automatic certificate renewal..."
    
    # Create renewal script
    cat > scripts/ssl-certificates/renew-certs.sh << 'EOF'
#!/bin/bash

DOMAIN="sport-lottery.example.com"
WEBROOT="/var/www/certbot"

# Renew certificates
certbot renew --webroot -w $WEBROOT --quiet

# Reload nginx if certificates were renewed
if [ $? -eq 0 ]; then
    docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
    echo "Certificates renewed and nginx reloaded"
else
    echo "Certificate renewal failed"
    exit 1
fi
EOF

    chmod +x scripts/ssl-certificates/renew-certs.sh
    
    # Add cron job (run twice daily)
    (crontab -l 2>/dev/null; echo "0 0,12 * * * $(pwd)/scripts/ssl-certificates/renew-certs.sh >> /var/log/cert-renewal.log 2>&1") | crontab -
    
    print_success "Auto-renewal configured (runs at 00:00 and 12:00 daily)"
}

# Verify SSL configuration
verify_ssl() {
    print_status "Verifying SSL configuration..."
    
    # Check if certificate files exist
    if [[ -f "nginx/ssl/sport-lottery.example.com.crt" && -f "nginx/ssl/sport-lottery.example.com.key" ]]; then
        print_success "SSL certificate files found"
        
        # Check certificate validity
        if openssl x509 -in nginx/ssl/sport-lottery.example.com.crt -text -noout | grep -q "Subject: CN=$DOMAIN"; then
            print_success "Certificate subject validation passed"
        else
            print_warning "Certificate subject validation failed"
        fi
        
        # Check certificate expiration
        EXPIRY_DATE=$(openssl x509 -in nginx/ssl/sport-lottery.example.com.crt -enddate -noout | cut -d= -f2)
        print_status "Certificate expires on: $EXPIRY_DATE"
    else
        print_error "SSL certificate files not found"
        exit 1
    fi
}

# Test nginx configuration
test_nginx_config() {
    print_status "Testing Nginx configuration..."
    
    # Validate nginx configuration
    if nginx -t 2>/dev/null; then
        print_success "Nginx configuration is valid"
    else
        # If nginx is not installed locally, check docker container
        if docker exec $NGINX_CONTAINER nginx -t 2>/dev/null; then
            print_success "Nginx configuration is valid (via Docker)"
        else
            print_warning "Could not validate Nginx configuration"
        fi
    fi
}

# Display certificate information
show_cert_info() {
    print_status "Certificate Information:"
    echo "==========================================="
    
    if [[ -f "nginx/ssl/sport-lottery.example.com.crt" ]]; then
        openssl x509 -in nginx/ssl/sport-lottery.example.com.crt -text -noout | grep -A 20 "Certificate:"
    fi
    
    echo "==========================================="
}

# Main execution
main() {
    local mode=${1:-auto}
    
    print_status "Starting SSL certificate setup..."
    print_status "Domain: $DOMAIN"
    print_status "Email: $EMAIL"
    
    check_root
    create_directories
    
    case $mode in
        "self-signed")
            generate_self_signed_cert
            ;;
        "letsencrypt")
            setup_letsencrypt
            setup_auto_renewal
            ;;
        "auto")
            # Try Let's Encrypt first, fallback to self-signed
            if command -v docker &> /dev/null; then
                setup_letsencrypt
                setup_auto_renewal
            else
                print_warning "Docker not available, using self-signed certificate"
                generate_self_signed_cert
            fi
            ;;
        *)
            print_error "Unknown mode: $mode"
            echo "Usage: $0 [self-signed|letsencrypt|auto]"
            exit 1
            ;;
    esac
    
    verify_ssl
    test_nginx_config
    show_cert_info
    
    print_success "SSL certificate setup completed!"
    print_status "Next steps:"
    echo "1. Update DNS records to point $DOMAIN to your server IP"
    echo "2. Update nginx configuration with your actual domain"
    echo "3. Restart nginx: docker-compose -f docker-compose.prod.yml restart nginx"
    echo "4. Test HTTPS access: https://$DOMAIN"
}

# Handle script interruption
trap 'print_warning "SSL setup interrupted"; exit 130' INT TERM

# Run main function
main "$@"