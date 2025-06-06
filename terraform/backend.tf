resource "kubernetes_deployment" "backend-config" {
  metadata {
    name      = "chatapp-backend-deployment"
    namespace = kubernetes_namespace.chat-app-ns.metadata[0].name
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "backend"
      }
    }

    template {
      metadata {
        labels = {
          app = "backend"
        }
      }

      spec {
        container {
          name  = "chatapp-backend"
          image = "amansharmaapp/chatapp-backend:latest"

          port {
            container_port = 5001
          }

          env {
            name  = "NODE_ENV"
            value = "production"
          }

          env {
            name  = "MONGODB_URI"
            value = "mongodb://mongodbadmin:secret@mongodb.chat-app.svc.cluster.local:27017/chatappdb?authSource=admin"
          }

          env {
            name = "JWT_SECRET"
            value_from {
              secret_key_ref {
                name = "chatapp-secret"
                key  = "jwt"
              }
            }
          }

          env {
            name  = "PORT"
            value = "5001"
          }

          image_pull_policy = "Always"
        }
      }
    }
  }
  depends_on = [
    kubernetes_deployment.mongo_config
  ]
}

resource "kubernetes_service" "backend-service-config" {
  metadata {
    name      = "backend"
    namespace = kubernetes_namespace.chat-app-ns.metadata[0].name
  }

  spec {
    selector = {
      app = "backend"
    }

    port {
      port        = 5001
      target_port = 5001
      protocol    = "TCP"
    }

    type = "ClusterIP"
  }
}
