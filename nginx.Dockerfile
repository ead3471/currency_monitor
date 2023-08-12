FROM nginx:1.19.3

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80