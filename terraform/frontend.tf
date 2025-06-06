resource "kubernetes_deployment" "frontend_config" {
  metadata {
    name      = "chatapp-frontend-deployment"
    namespace = kubernetes_namespace.chat-app-ns.metadata[0].name
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "frontend"
      }
    }

    template {
      metadata {
        labels = {
          app = "frontend"
        }
      }

      spec {
        container {
          name  = "chatapp-frontend"
          image = "amansharmaapp/chatapp-frontend:latest"

          port {
            container_port = 80
          }

          env {
            name  = "NODE_ENV"
            value = "production"
          }
        }
      }
    }
  }
  depends_on = [
    kubernetes_deployment.backend-config
  ]
}

resource "kubernetes_service" "frontend_service_config" {
  metadata {
    name      = "frontend"
    namespace = kubernetes_namespace.chat-app-ns.metadata[0].name
  }

  spec {
    selector = {
      app = "frontend"
    }
    port {
      port        = 80
      target_port = 80
      protocol    = "TCP"
    }

    type = "ClusterIP"
  }
}
